package com.cok.console

import android.annotation.SuppressLint
import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.lifecycleScope
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import com.cok.console.net.ConsoleRepository
import com.cok.console.ui.CokApp
import com.cok.console.ui.ServerState
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.net.HttpURLConnection
import java.net.URL
import java.util.UUID

/**
 * Native host for the embedded COK console.
 *
 * The Python control server and the shared desktop page are untouched. This
 * activity boots Chaquopy, waits for the loopback server, then renders a native
 * Compose shell that talks to the same local HTTP API the web page uses.
 */
class MainActivity : ComponentActivity() {

    private var serverState by mutableStateOf<ServerState>(ServerState.Booting)

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            CokApp(
                serverState = serverState,
                repositoryFor = { base, token -> ConsoleRepository(base, token) },
            )
        }

        lifecycleScope.launch { boot() }
    }

    private suspend fun boot() {
        val result = withContext(Dispatchers.IO) {
            runCatching {
                if (!Python.isStarted()) {
                    Python.start(AndroidPlatform(applicationContext))
                }
                val token = UUID.randomUUID().toString().replace("-", "")
                val url = Python.getInstance()
                    .getModule("android_entry")
                    .callAttr("start", filesDir.absolutePath, PORT, token)
                    .toString()
                waitForServer(url)
                val activeToken = Uri.parse(url).getQueryParameter("t")
                    ?: error("本地控制台未提供访问令牌")
                url to activeToken
            }
        }
        serverState = result.fold(
            onSuccess = { (url, token) -> ServerState.Ready(baseUrl = url.substringBefore("/?"), token = token, fullUrl = url) },
            onFailure = { ServerState.Failed(it.message ?: "控制台启动失败") },
        )
    }

    /** Poll the loopback server until it answers, so the UI never loads a blank page. */
    private fun waitForServer(url: String) {
        repeat(SERVER_WAIT_ATTEMPTS) {
            try {
                val conn = URL(url).openConnection() as HttpURLConnection
                conn.connectTimeout = 250
                conn.readTimeout = 250
                conn.requestMethod = "GET"
                val status = conn.responseCode
                conn.disconnect()
                // Any HTTP reply proves the server is up; 403 just means token gating.
                if (status in 200..499) return
            } catch (_: Exception) {
                Thread.sleep(200)
            }
        }
        throw IllegalStateException("控制台服务启动超时，请重开应用")
    }

    private companion object {
        const val PORT = 18770
        const val SERVER_WAIT_ATTEMPTS = 450
    }
}
