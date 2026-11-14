package com.cok.console

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.IBinder
import android.provider.Settings
import androidx.core.content.ContextCompat
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import com.cok.console.net.ConsoleRepository
import com.cok.console.ui.ConsoleSnapshot
import com.cok.console.ui.Severity
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import java.net.HttpURLConnection
import java.net.URL
import java.util.UUID
import org.json.JSONObject

/** Keeps the loopback console alive and reports newly detected high-risk states. */
class BackgroundMonitorService : Service() {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private var monitorJob: Job? = null
    private lateinit var preferences: android.content.SharedPreferences

    override fun onCreate() {
        super.onCreate()
        preferences = getSharedPreferences(PREFERENCES, Context.MODE_PRIVATE)
        createChannels()
        startAsForeground("正在准备后台守护")
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == ACTION_STOP) {
            preferences.edit().putBoolean(KEY_ENABLED, false).apply()
            stopForeground(STOP_FOREGROUND_REMOVE)
            stopSelf()
            return START_NOT_STICKY
        }
        preferences.edit().putBoolean(KEY_ENABLED, true).apply()
        if (monitorJob == null) monitorJob = scope.launch { monitorLoop() }
        return START_STICKY
    }

    override fun onDestroy() {
        monitorJob?.cancel()
        scope.coroutineContext[Job]?.cancel()
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private suspend fun monitorLoop() {
        while (scope.isActive) {
            pollOnce()
            delay(POLL_INTERVAL_MS)
        }
    }

    private suspend fun pollOnce() {
        try {
            val ready = ensureServer()
            val repository = ConsoleRepository(ready.baseUrl, ready.token)
            // A state fetch alone could be stale. This invokes the console's
            // regular poll, including any automation the user already enabled.
            //
            // ⚠️ **必须刷所有托管账号, 不是只刷当前在看的那个**:
            //    `refresh-now` 是**引擎级**操作, 只作用于 view_engine()(当前
            //    查看的账号)。以前这里只发它 ⇒ 后台开着也只轮询 1 个号,
            //    其余托管账号永远停在旧数据上("后台运行不生效")。
            //    `refresh-all` 由控制台侧对并行集 ∪ 查看账号各发一次, 并行执行。
            repository.action(JSONObject().put("action", "refresh-all")).getOrThrow()
            val snapshot = repository.fetchState().getOrThrow()
            val console = ConsoleSnapshot.from(snapshot)
            val risks = console.triage.filter { it.severity == Severity.RISK }
            // 当前查看账号的风险(triage 只覆盖在看的号)
            val lines = risks.map { "${it.title}:${it.detail}" }.toMutableList()
            val titles = risks.map { it.title }.toMutableList()
            // 后台并行账号: triage 不覆盖它们, 用每账号摘要补一轮按账号的风险扫描,
            // 否则"在看 A 号, B 号掉罩/被打"永远不会通知。
            console.accounts.forEach { acct ->
                val s = acct.summary ?: return@forEach
                if (!acct.isRunning || acct.isActive) return@forEach
                val acctRisks = buildList {
                    if (s.error.isNotBlank()) add("连接异常")
                    else if (s.stale) add("久无响应")
                    if (!s.hasShield && !s.hunting) add("无保护罩")
                }
                if (acctRisks.isNotEmpty()) {
                    titles += "${acct.label}: ${acctRisks.joinToString("、")}"
                    lines += "${acct.label}:${acctRisks.joinToString("、")}"
                }
            }
            val signature = lines.joinToString("|")
            val previous = preferences.getString(KEY_RISK_SIGNATURE, null)
            if (preferences.getBoolean(KEY_RISK_ALERTS, false) && signature.isNotBlank() && signature != previous) {
                notifyRisk(titles.joinToString("；"))
            }
            preferences.edit()
                .putString(KEY_RISK_SIGNATURE, signature)
                .putLong(KEY_LAST_POLL, System.currentTimeMillis())
                .apply()
            val riskCount = titles.size
            startAsForeground(if (riskCount == 0) "后台守护运行中 · 状态正常" else "后台守护运行中 · 发现 ${riskCount} 项风险")
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (error: Exception) {
            // ⚠️ 新版控制台才有 refresh-all。老控制台会回"未知操作", 这里
            //    退回只刷当前查看账号 —— 至少不比改造前更差。
            try {
                val ready = ensureServer()
                val repository = ConsoleRepository(ready.baseUrl, ready.token)
                repository.action(JSONObject().put("action", "refresh-now")).getOrThrow()
            } catch (_: Exception) {
                // 忽略: 下面统一记时间戳
            }
            preferences.edit().putLong(KEY_LAST_POLL, System.currentTimeMillis()).apply()
            startAsForeground("后台守护运行中 · 等待下次检查")
        }
    }

    private fun ensureServer(): ServerAccess {
        if (!Python.isStarted()) Python.start(AndroidPlatform(applicationContext))
        val requestedToken = UUID.randomUUID().toString().replace("-", "")
        val url = Python.getInstance().getModule("android_entry")
            .callAttr("start", filesDir.absolutePath, PORT, requestedToken)
            .toString()
        waitForServer(url)
        val token = android.net.Uri.parse(url).getQueryParameter("t")
            ?: error("本地控制台未提供访问令牌")
        return ServerAccess(url.substringBefore("/?"), token)
    }

    private fun waitForServer(url: String) {
        repeat(SERVER_WAIT_ATTEMPTS) {
            try {
                val connection = (URL(url).openConnection() as HttpURLConnection).apply {
                    connectTimeout = 250
                    readTimeout = 250
                    requestMethod = "GET"
                }
                val status = connection.responseCode
                connection.disconnect()
                if (status in 200..499) return
            } catch (_: Exception) {
                Thread.sleep(200)
            }
        }
        error("本地控制台启动超时")
    }

    private fun createChannels() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return
        val manager = getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(
            NotificationChannel(MONITOR_CHANNEL, "后台守护", NotificationManager.IMPORTANCE_LOW).apply {
                description = "后台检查 COK 风险状态的常驻通知"
                setShowBadge(false)
            },
        )
        manager.createNotificationChannel(
            NotificationChannel(RISK_CHANNEL, "风险提醒", NotificationManager.IMPORTANCE_HIGH).apply {
                description = "保护罩、连接等需要立即处理的状态"
            },
        )
    }

    private fun startAsForeground(detail: String) {
        val notification = ongoingNotification(detail)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            startForeground(ONGOING_NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE)
        } else {
            startForeground(ONGOING_NOTIFICATION_ID, notification)
        }
    }

    private fun ongoingNotification(detail: String): Notification = Notification.Builder(this, MONITOR_CHANNEL)
        .setSmallIcon(android.R.drawable.stat_notify_sync)
        .setContentTitle("COK 控制台后台守护")
        .setContentText(detail)
        .setContentIntent(openAppIntent())
        .setOngoing(true)
        .addAction(android.R.drawable.ic_menu_close_clear_cancel, "停止", stopIntent())
        .build()

    private fun notifyRisk(detail: String) {
        val manager = getSystemService(NotificationManager::class.java)
        manager.notify(
            RISK_NOTIFICATION_ID,
            Notification.Builder(this, RISK_CHANNEL)
                .setSmallIcon(android.R.drawable.stat_notify_error)
                .setContentTitle("COK 控制台需要处理")
                .setContentText(detail)
                .setStyle(Notification.BigTextStyle().bigText(detail))
                .setContentIntent(openAppIntent())
                .setAutoCancel(true)
                .setCategory(Notification.CATEGORY_ERROR)
                .build(),
        )
    }

    private fun openAppIntent(): PendingIntent = PendingIntent.getActivity(
        this, 0,
        Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP
        },
        PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
    )

    private fun stopIntent(): PendingIntent = PendingIntent.getService(
        this, 1,
        Intent(this, BackgroundMonitorService::class.java).setAction(ACTION_STOP),
        PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
    )

    private data class ServerAccess(val baseUrl: String, val token: String)

    companion object {
        private const val ACTION_STOP = "com.cok.console.action.STOP_BACKGROUND_MONITOR"
        private const val PREFERENCES = "console-ui"
        const val KEY_ENABLED = "background-monitoring"
        const val KEY_RISK_ALERTS = "risk-alerts"
        private const val KEY_RISK_SIGNATURE = "background-risk-signature"
        private const val KEY_LAST_POLL = "background-last-poll"
        private const val MONITOR_CHANNEL = "background-monitor"
        private const val RISK_CHANNEL = "risk-alerts"
        private const val ONGOING_NOTIFICATION_ID = 3102
        private const val RISK_NOTIFICATION_ID = 3103
        private const val PORT = 18770
        private const val SERVER_WAIT_ATTEMPTS = 450
        private const val POLL_INTERVAL_MS = 5 * 60 * 1000L

        fun start(context: Context) {
            ContextCompat.startForegroundService(context, Intent(context, BackgroundMonitorService::class.java))
        }

        fun stop(context: Context) {
            context.stopService(Intent(context, BackgroundMonitorService::class.java))
        }

        fun openNotificationSettings(context: Context) {
            context.startActivity(
                Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS)
                    .putExtra(Settings.EXTRA_APP_PACKAGE, context.packageName)
                    .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK),
            )
        }
    }
}
