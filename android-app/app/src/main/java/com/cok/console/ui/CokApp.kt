package com.cok.console.ui

import androidx.activity.compose.BackHandler
import android.Manifest
import android.content.Context
import android.content.ContentValues
import android.content.pm.PackageManager
import android.os.Build
import android.provider.MediaStore
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Build
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Settings
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.platform.LocalContext
import androidx.core.content.ContextCompat
import com.cok.console.BackgroundMonitorService
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.compose.runtime.collectAsState
import kotlinx.coroutines.delay

private enum class Tab(val label: String, val icon: ImageVector) {
    HOME("状态", Icons.Filled.Home),
    OPERATIONS("操作", Icons.Filled.Build),
    ACCOUNTS("账号", Icons.Filled.Person),
    MORE("更多", Icons.Filled.Settings),
    WEB_CONSOLE("高级控制台", Icons.Filled.Settings),
}

/** Root of the native shell: boot states, bottom nav, and screen hosting. */
@Composable
fun CokApp(
    serverState: ServerState,
    repositoryFor: RepositoryFactory,
) {
    CokTheme {
        when (serverState) {
            is ServerState.Booting -> BootScreen("正在启动本地控制台…")
            is ServerState.Failed -> BootScreen(serverState.message, isError = true)
            is ServerState.Ready -> ReadyShell(serverState, repositoryFor)
        }
    }
}

@Composable
private fun ReadyShell(ready: ServerState.Ready, repositoryFor: RepositoryFactory) {
    val repo = remember(ready.baseUrl, ready.token) { repositoryFor(ready.baseUrl, ready.token) }
    val vm: ConsoleViewModel = viewModel(
        key = ready.token,
        factory = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T = ConsoleViewModel(repo) as T
        },
    )
    LaunchedEffect(Unit) { vm.start() }

    val ui by vm.state.collectAsState()
    var tab by rememberSaveable { mutableStateOf(Tab.HOME) }
    var operationsFocus by rememberSaveable { mutableStateOf<OperationsFocus?>(null) }
    val snackbar = remember { SnackbarHostState() }
    val context = LocalContext.current
    val preferences = remember { context.getSharedPreferences("console-ui", Context.MODE_PRIVATE) }
    var alertsEnabled by rememberSaveable { mutableStateOf(preferences.getBoolean("risk-alerts", false)) }
    var backgroundMonitoringEnabled by rememberSaveable {
        mutableStateOf(preferences.getBoolean(BackgroundMonitorService.KEY_ENABLED, false))
    }
    var startBackgroundAfterPermission by rememberSaveable { mutableStateOf(false) }
    var lastRiskSignature by remember { mutableStateOf<String?>(null) }
    val alertController = remember { LocalAlertController(context.applicationContext) }
    val notificationPermission = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission(),
    ) { granted ->
        alertsEnabled = granted
        preferences.edit().putBoolean("risk-alerts", granted).apply()
        if (startBackgroundAfterPermission) {
            startBackgroundAfterPermission = false
            if (granted) {
                backgroundMonitoringEnabled = true
                preferences.edit().putBoolean(BackgroundMonitorService.KEY_ENABLED, true).apply()
                BackgroundMonitorService.start(context)
            }
        }
    }

    val riskItems = ui.snapshot?.triage.orEmpty().filter { it.severity == Severity.RISK }
    val riskSignature = riskItems.joinToString("|") { "${it.title}:${it.detail}" }.ifBlank { null }
    LaunchedEffect(alertsEnabled, riskSignature) {
        if (!alertsEnabled) {
            lastRiskSignature = null
        } else if (riskSignature != null && riskSignature != lastRiskSignature) {
            alertController.notifyRisk("COK 控制台需要处理", riskItems.joinToString("；") { it.title })
            lastRiskSignature = riskSignature
        }
    }

    LaunchedEffect(ui.exportPayload) {
        val payload = ui.exportPayload ?: return@LaunchedEffect
        // 原生导出与 WebView 控制台里的导出落到同一个目录: 下载/COK/
        val result = saveExportToDownloads(context, payload.filename, payload.bytes)
        vm.markExportSaved(result)
    }

    BackHandler(enabled = tab == Tab.WEB_CONSOLE) {
        tab = Tab.OPERATIONS
    }

    LaunchedEffect(ui.actionMessage) {
        ui.actionMessage?.let {
            snackbar.showSnackbar(it)
            vm.clearActionMessage()
        }
    }

    LaunchedEffect(ui.actionOutcome) {
        if (ui.actionOutcome?.snapshotVerified == true || ui.actionOutcome?.succeeded == false) {
            delay(12_000)
            vm.clearActionOutcome()
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbar) },
        bottomBar = {
            NavigationBar(containerColor = CokPalette.surface) {
                NavigationBarItem(
                    selected = tab == Tab.HOME,
                    onClick = { tab = Tab.HOME },
                    icon = { Icon(Tab.HOME.icon, contentDescription = null) },
                    label = { Text(Tab.HOME.label) },
                    colors = navColors(),
                )
                NavigationBarItem(
                    selected = tab == Tab.OPERATIONS,
                    onClick = { tab = Tab.OPERATIONS },
                    icon = { Icon(Tab.OPERATIONS.icon, contentDescription = null) },
                    label = { Text(Tab.OPERATIONS.label) },
                    colors = navColors(),
                )
                NavigationBarItem(
                    selected = tab == Tab.ACCOUNTS,
                    onClick = { tab = Tab.ACCOUNTS },
                    icon = { Icon(Tab.ACCOUNTS.icon, contentDescription = null) },
                    label = { Text(Tab.ACCOUNTS.label) },
                    colors = navColors(),
                )
                NavigationBarItem(
                    selected = tab == Tab.MORE,
                    onClick = { tab = Tab.MORE },
                    icon = { Icon(Tab.MORE.icon, contentDescription = null) },
                    label = { Text(Tab.MORE.label) },
                    colors = navColors(),
                )
            }
        },
    ) { padding ->
        Box(Modifier.fillMaxSize().padding(padding)) {
            when (tab) {
                Tab.HOME -> HomeScreen(
                    ui = ui,
                    onRefresh = vm::refresh,
                    onAction = vm::runAction,
                    onOpenOperations = { focus ->
                        operationsFocus = focus
                        tab = Tab.OPERATIONS
                    },
                    onOpenMore = { tab = Tab.MORE },
                )
                Tab.OPERATIONS -> OperationsScreen(
                    ui = ui,
                    backgroundMonitoringEnabled = backgroundMonitoringEnabled,
                    initialFocus = operationsFocus,
                    onFocusHandled = { operationsFocus = null },
                    onAction = vm::runAction,
                    onSetAutomation = vm::setAutomationSetting,
                    onSaveAutomationPolicy = vm::saveAutomationPolicy,
                    onRecheckAutomation = vm::recheckAutomation,
                    onSaveHuntPlan = vm::saveHuntPlan,
                    onUseShield = vm::useShield,
                    onStartHunt = vm::startHunt,
                    onStopHunt = vm::stopHunt,
                    onSpeedUpWithItem = vm::speedUpWithItem,
                    onSpeedUpWithGold = vm::speedUpWithGold,
                    onClaimSkyReward = vm::claimSkyReward,
                    onStartSkyExplore = vm::startSkyExplore,
                    onLoadRally = vm::loadRally,
                    onStartRally = vm::startRally,
                    onOpenConsole = { tab = Tab.WEB_CONSOLE },
                )
                Tab.ACCOUNTS -> AccountScreen(
                    ui = ui,
                    onRefresh = vm::refresh,
                    onSwitch = vm::switchAccount,
                    onSetParallel = vm::setAccountParallel,
                    onSetAccountsParallel = vm::setAccountsParallel,
                    onSetPriority = vm::setAccountPriority,
                    onImport = vm::importDeviceAccounts,
                    onRename = vm::renameAccount,
                    onRemove = vm::removeAccount,
                    onChannelLogin = vm::loginChannelAccount,
                    onChannelAdd = vm::addChannelAccounts,
                    onClearChannelLogin = vm::clearChannelLogin,
                    onLoadChannels = vm::loadChannelOptions,
                )
                Tab.MORE -> MoreScreen(
                    ui = ui,
                    onRefresh = vm::refresh,
                    onReconnect = vm::reconnect,
                    onDisconnect = vm::disconnect,
                    alertsEnabled = alertsEnabled,
                    onSetAlertsEnabled = { enabled ->
                        val permissionGranted = Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU ||
                            ContextCompat.checkSelfPermission(context, Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED
                        if (enabled && !permissionGranted) {
                            notificationPermission.launch(Manifest.permission.POST_NOTIFICATIONS)
                        } else {
                            alertsEnabled = enabled
                            preferences.edit().putBoolean("risk-alerts", enabled).apply()
                        }
                    },
                    backgroundMonitoringEnabled = backgroundMonitoringEnabled,
                    onSetBackgroundMonitoring = { enabled ->
                        val permissionGranted = Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU ||
                            ContextCompat.checkSelfPermission(context, Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED
                        if (enabled && !permissionGranted) {
                            startBackgroundAfterPermission = true
                            notificationPermission.launch(Manifest.permission.POST_NOTIFICATIONS)
                        } else {
                            backgroundMonitoringEnabled = enabled
                            preferences.edit().putBoolean(BackgroundMonitorService.KEY_ENABLED, enabled).apply()
                            if (enabled) {
                                alertsEnabled = true
                                preferences.edit().putBoolean("risk-alerts", true).apply()
                                BackgroundMonitorService.start(context)
                            } else {
                                BackgroundMonitorService.stop(context)
                            }
                        }
                    },
                    onStartScan = vm::startScan,
                    onStopScan = vm::stopScan,
                    onRefreshScan = vm::refreshScanStatus,
                    onLocate = vm::locatePlayer,
                    onExport = vm::exportPlayers,
                )
                Tab.WEB_CONSOLE -> ConsoleWebScreen(ready.fullUrl)
            }
        }
    }
}

@Composable
private fun navColors() = NavigationBarItemDefaults.colors(
    selectedIconColor = CokPalette.accentText,
    selectedTextColor = CokPalette.accentText,
    indicatorColor = CokPalette.surfaceHigher,
    unselectedIconColor = CokPalette.dim2,
    unselectedTextColor = CokPalette.dim2,
)

@Composable
private fun BootScreen(message: String, isError: Boolean = false) {
    Box(
        Modifier
            .fillMaxSize(),
        contentAlignment = Alignment.Center,
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            if (!isError) {
                CircularProgressIndicator(Modifier.size(34.dp), color = CokPalette.accent, strokeWidth = 3.dp)
            }
            Text(
                message,
                color = if (isError) CokPalette.err else CokPalette.dim,
                fontSize = 14.sp,
                fontWeight = if (isError) FontWeight.SemiBold else FontWeight.Normal,
            )
        }
    }
}
