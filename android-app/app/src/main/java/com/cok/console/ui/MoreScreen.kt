package com.cok.console.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/** Low-frequency tools and diagnostics, with the legacy console as a fallback. */
@Composable
fun MoreScreen(
    ui: HomeUiState,
    onRefresh: () -> Unit,
    onReconnect: () -> Unit,
    onDisconnect: () -> Unit,
    alertsEnabled: Boolean,
    onSetAlertsEnabled: (Boolean) -> Unit,
    backgroundMonitoringEnabled: Boolean,
    onSetBackgroundMonitoring: (Boolean) -> Unit,
    onStartScan: (Int, Boolean) -> Unit,
    onStopScan: () -> Unit,
    onRefreshScan: () -> Unit,
    onLocate: (String, Boolean) -> Unit,
    onExport: (Boolean) -> Unit,
) {
    val snapshot = ui.snapshot
    var confirmDisconnect by rememberSaveable { mutableStateOf(false) }
    var confirmStartScan by rememberSaveable { mutableStateOf(false) }
    var showEvents by rememberSaveable { mutableStateOf(false) }
    var showMapTools by rememberSaveable { mutableStateOf(false) }
    var locateName by rememberSaveable { mutableStateOf("") }
    var scanStep by rememberSaveable { mutableStateOf(12) }
    var scanResume by rememberSaveable { mutableStateOf(false) }
    var exportRealOnly by rememberSaveable { mutableStateOf(true) }
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp, 12.dp, 16.dp, 112.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.weight(1f)) {
                    Text("更多", color = CokPalette.fg, fontSize = 22.sp, fontWeight = FontWeight.Bold)
                    Spacer(Modifier.height(5.dp))
                    Text("连接、提醒与诊断", color = CokPalette.dim, fontSize = 13.sp)
                }
                IconButton(onClick = onRefresh, enabled = !ui.refreshing) {
                    Icon(Icons.Filled.Refresh, contentDescription = "刷新状态", tint = CokPalette.accentText)
                }
            }
        }
        item { MoreSection("连接") }
        item {
            Column(Modifier.fillMaxWidth().clip(RoundedCornerShape(10.dp)).background(CokPalette.surface).border(1.dp, CokPalette.line, RoundedCornerShape(10.dp)).padding(14.dp)) {
                Text(snapshot?.connectionLabel ?: "正在检查连接", color = severityColor(snapshot?.connectionSeverity ?: Severity.INFO), fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
                Spacer(Modifier.height(5.dp))
                Text(snapshot?.account?.let { "当前账号 · $it" } ?: "尚未读取当前账号", color = CokPalette.dim, fontSize = 12.sp, maxLines = 1, overflow = TextOverflow.Ellipsis)
                Spacer(Modifier.height(12.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
                    OutlinedButton(onClick = onReconnect, enabled = ui.operationInFlight == null, modifier = Modifier.weight(1f), shape = RoundedCornerShape(8.dp)) { Text("重新连接", color = CokPalette.accentText) }
                    OutlinedButton(onClick = { confirmDisconnect = true }, enabled = ui.operationInFlight == null, modifier = Modifier.weight(1f), shape = RoundedCornerShape(8.dp)) { Text("断开", color = CokPalette.err) }
                }
            }
        }
        item { MoreSection("记录") }
        item { MoreRow("运行记录", "查看最近的控制台事件", onClick = { showEvents = !showEvents }) }
        if (showEvents) {
            val events = snapshot?.recentEvents.orEmpty()
            if (events.isEmpty()) item { EmptyEvents() } else items(events, key = { "${it.time}-${it.message}" }) { EventRow(it) }
        }
        item { MoreSection("诊断工具") }
        item {
            MoreRow(
                "地图与定位",
                "${snapshot?.mapIndex?.playerCount ?: 0} 名已索引玩家${if (snapshot?.mapIndex?.isScanning == true) " · 扫描中" else ""}",
                onClick = {
                    showMapTools = !showMapTools
                    if (showMapTools) onRefreshScan()
                },
            )
        }
        if (showMapTools) {
            item {
                MapTools(
                    map = ui.scanStatus ?: snapshot?.mapIndex,
                    scanBusy = ui.scanInFlight,
                    locateBusy = ui.locateInFlight,
                    locateName = locateName,
                    locateResult = ui.locateResult,
                    onLocateNameChange = { locateName = it },
                    onLocate = { onLocate(locateName, false) },
                    onScanNearby = { onLocate(locateName, true) },
                    onStartScan = { confirmStartScan = true },
                    onStopScan = onStopScan,
                    onRefresh = onRefreshScan,
                    exportBusy = ui.exportInFlight,
                    onExport = onExport,
                    history = ui.scanHistory,
                    scanStep = scanStep,
                    onScanStepChange = { scanStep = it },
                    scanResume = scanResume,
                    onScanResumeChange = { scanResume = it },
                    exportRealOnly = exportRealOnly,
                    onExportRealOnlyChange = { exportRealOnly = it },
                )
            }
        }
        item { MoreSection("提醒") }
        item {
            Row(
                Modifier.fillMaxWidth().clip(RoundedCornerShape(10.dp)).background(CokPalette.surface).border(1.dp, CokPalette.line, RoundedCornerShape(10.dp)).padding(14.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Column(Modifier.weight(1f)) {
                    Text("高风险提醒", color = CokPalette.fg, fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
                    Spacer(Modifier.height(3.dp))
                    Text("保护罩、连接和需要人工处理的自动化异常会通知", color = CokPalette.dim, fontSize = 12.sp, lineHeight = 17.sp)
                }
                Switch(checked = alertsEnabled, onCheckedChange = onSetAlertsEnabled)
            }
        }
        item {
            Row(
                Modifier.fillMaxWidth().clip(RoundedCornerShape(10.dp)).background(CokPalette.surface).border(1.dp, CokPalette.line, RoundedCornerShape(10.dp)).padding(14.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Column(Modifier.weight(1f)) {
                    Text("后台风险守护", color = CokPalette.fg, fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
                    Spacer(Modifier.height(3.dp))
                    Text(
                        if (backgroundMonitoringEnabled) "运行中 · 每 5 分钟刷新一次；沿用已开启的自动规则，通知栏可停止"
                        else "关闭应用后继续刷新风险状态；会显示常驻通知并增加少量耗电",
                        color = CokPalette.dim,
                        fontSize = 12.sp,
                        lineHeight = 17.sp,
                    )
                }
                Switch(checked = backgroundMonitoringEnabled, onCheckedChange = onSetBackgroundMonitoring)
            }
        }
    }
    if (confirmDisconnect) AlertDialog(
        onDismissRequest = { confirmDisconnect = false },
        title = { Text("断开游戏连接") },
        text = { Text("断开后将停止本次连接与轮询，稍后可在此重新连接。") },
        confirmButton = { Button(onClick = { onDisconnect(); confirmDisconnect = false }, colors = ButtonDefaults.buttonColors(containerColor = CokPalette.err)) { Text("确认断开") } },
        dismissButton = { OutlinedButton(onClick = { confirmDisconnect = false }) { Text("取消") } },
    )
    if (confirmStartScan) AlertDialog(
        onDismissRequest = { confirmStartScan = false },
        title = { Text("开始全图扫描") },
        text = {
            Text(
                "步长 $scanStep" + (if (scanResume) " · 从上次断点继续" else " · 全图重扫") + "。" +
                    "扫描会在独立进程中持续运行，并占用当前账号连接。运行期间不能自动打怪；你可以随时在这里停止，断点会保留。",
            )
        },
        confirmButton = {
            Button(onClick = { onStartScan(scanStep, scanResume); confirmStartScan = false }) { Text("开始扫描") }
        },
        dismissButton = { OutlinedButton(onClick = { confirmStartScan = false }) { Text("取消") } },
    )
}

@Composable
private fun MapTools(
    map: MapIndexStatus?,
    scanBusy: Boolean,
    locateBusy: Boolean,
    locateName: String,
    locateResult: LocateResult?,
    onLocateNameChange: (String) -> Unit,
    onLocate: () -> Unit,
    onScanNearby: () -> Unit,
    onStartScan: () -> Unit,
    onStopScan: () -> Unit,
    onRefresh: () -> Unit,
    exportBusy: Boolean,
    onExport: (Boolean) -> Unit,
    history: List<ScanHistoryRun>,
    scanStep: Int,
    onScanStepChange: (Int) -> Unit,
    scanResume: Boolean,
    onScanResumeChange: (Boolean) -> Unit,
    exportRealOnly: Boolean,
    onExportRealOnlyChange: (Boolean) -> Unit,
) {
    Column(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(10.dp)).background(CokPalette.surface)
            .border(1.dp, CokPalette.line, RoundedCornerShape(10.dp)).padding(14.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text("地图索引", color = CokPalette.fg, fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
                Text(
                    if (map?.isScanning == true) "扫描中 · ${map.requestsDone}/${map.requestsTotal} 次请求" else "已索引 ${map?.playerCount ?: 0} 名玩家",
                    color = CokPalette.dim,
                    fontSize = 12.sp,
                )
            }
            IconButton(onClick = onRefresh, enabled = !scanBusy) {
                Icon(Icons.Filled.Refresh, contentDescription = "刷新扫描状态", tint = CokPalette.accentText)
            }
        }
        if (map?.isScanning == true) {
            LinearProgressIndicator(
                progress = { map.percent / 100f },
                modifier = Modifier.fillMaxWidth(),
                color = CokPalette.accent,
                trackColor = CokPalette.surfaceHigher,
            )
            OutlinedButton(onClick = onStopScan, enabled = !scanBusy, modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(8.dp)) {
                Text("停止全图扫描", color = CokPalette.err)
            }
        } else {
            val health = listOfNotNull(
                map?.errors?.takeIf { it > 0 }?.let { "失败 $it" },
                map?.mismatched?.takeIf { it > 0 }?.let { "错位 $it" },
                map?.dropped?.takeIf { it > 0 }?.let { "越界 $it" },
            ).joinToString(" · ")
            if (health.isNotBlank()) Text("上次扫描健康：$health", color = CokPalette.warn, fontSize = 11.sp)
            // 步长: world.get 实测覆盖只有 ±12 格, 步长必须 ≤ 覆盖直径, 否则会漏城
            Text("步长（越大越快但会漏城，推荐 12）", color = CokPalette.dim2, fontSize = 11.sp)
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                listOf(12 to "12 推荐", 20 to "20 快", 26 to "26 更快").forEach { (value, label) ->
                    val selected = scanStep == value
                    OutlinedButton(
                        onClick = { onScanStepChange(value) },
                        enabled = !scanBusy,
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(8.dp),
                        colors = ButtonDefaults.outlinedButtonColors(
                            containerColor = if (selected) CokPalette.accent.copy(alpha = .14f) else Color.Transparent,
                        ),
                    ) { Text(label, color = if (selected) CokPalette.accentText else CokPalette.dim, fontSize = 12.sp) }
                }
            }
            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
                Text("从上次断点继续（否则清空重扫）", color = CokPalette.dim2, fontSize = 11.sp, modifier = Modifier.weight(1f))
                Switch(checked = scanResume, onCheckedChange = onScanResumeChange, enabled = !scanBusy)
            }
            OutlinedButton(onClick = onStartScan, enabled = !scanBusy, modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(8.dp)) {
                Text("开始全图扫描", color = CokPalette.accentText)
            }
        }
        Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
            Text("导出仅含真实玩家（排除 NPC/怪物城）", color = CokPalette.dim2, fontSize = 11.sp, modifier = Modifier.weight(1f))
            Switch(checked = exportRealOnly, onCheckedChange = onExportRealOnlyChange, enabled = !exportBusy && !scanBusy)
        }
        OutlinedButton(onClick = { onExport(exportRealOnly) }, enabled = !exportBusy && !scanBusy, modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(8.dp)) {
            if (exportBusy) CircularProgressIndicator(Modifier.height(18.dp), color = CokPalette.accentText, strokeWidth = 2.dp)
            else Text("导出已索引玩家 Excel", color = CokPalette.accentText)
        }
        Spacer(Modifier.height(2.dp))
        Text("玩家定位", color = CokPalette.fg, fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
        OutlinedTextField(
            value = locateName,
            onValueChange = onLocateNameChange,
            modifier = Modifier.fillMaxWidth(),
            label = { Text("玩家名称") },
            singleLine = true,
        )
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
            OutlinedButton(onClick = onScanNearby, enabled = !locateBusy && !scanBusy, modifier = Modifier.weight(1f), shape = RoundedCornerShape(8.dp)) {
                if (locateBusy) CircularProgressIndicator(Modifier.height(18.dp), color = CokPalette.accentText, strokeWidth = 2.dp)
                else Text("扫描附近", color = CokPalette.accentText)
            }
            Button(onClick = onLocate, enabled = locateName.isNotBlank() && !locateBusy, modifier = Modifier.weight(1f), shape = RoundedCornerShape(8.dp)) {
                if (locateBusy) CircularProgressIndicator(Modifier.height(18.dp), color = Color.White, strokeWidth = 2.dp)
                else Text("查询坐标")
            }
        }
        locateResult?.let { result -> LocateResultView(result) }
        if (history.isNotEmpty()) {
            Spacer(Modifier.height(2.dp))
            Text("扫描历史", color = CokPalette.fg, fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
            history.take(8).forEach { run -> ScanHistoryRow(run) }
        }
    }
}

private fun formatScanTime(epochSeconds: Long): String =
    SimpleDateFormat("MM-dd HH:mm", Locale.getDefault()).format(Date(epochSeconds * 1000L))

@Composable
private fun ScanHistoryRow(run: ScanHistoryRun) {
    val statusLabel = when (run.status) {
        "completed" -> "完成"
        "interrupted" -> "中断"
        "running" -> "进行中"
        else -> run.status.ifBlank { "未知" }
    }
    val statusColor = when (run.status) {
        "completed" -> CokPalette.ok
        "interrupted" -> CokPalette.warn
        "running" -> CokPalette.accentText
        else -> CokPalette.dim
    }
    val scope = if (run.radius > 0) "范围 ${run.radius}" else "全图"
    Row(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(8.dp)).background(CokPalette.surfaceHigher).padding(10.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(Modifier.weight(1f)) {
            Text(
                "$scope · 步长 ${run.step} · ${run.players} 玩家" +
                    (if (run.realPlayers > 0) "（真实 ${run.realPlayers}）" else ""),
                color = CokPalette.fg, fontSize = 12.sp,
            )
            Text(
                "请求 ${run.requestsDone}/${run.requestsTotal}" +
                    (if (run.errors > 0) " · 失败 ${run.errors}" else "") +
                    (if (run.startedAt > 0) " · " + formatScanTime(run.startedAt) else ""),
                color = CokPalette.dim2, fontSize = 11.sp,
            )
        }
        Text(statusLabel, color = statusColor, fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
    }
}

@Composable
private fun LocateResultView(result: LocateResult) {
    val source = when (result.source) {
        "index" -> "本地索引"
        "index+verified" -> "索引已实时校验"
        "scan" -> "附近扫描"
        "item" -> "道具查询"
        else -> "定位结果"
    }
    Column(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(8.dp)).background(CokPalette.surfaceHigher).padding(10.dp),
        verticalArrangement = Arrangement.spacedBy(5.dp),
    ) {
        Text("$source · ${result.message}", color = CokPalette.dim, fontSize = 11.sp)
        if (result.scanRequests > 0) Text("扫描 ${result.scanRequests} 次请求", color = CokPalette.dim2, fontSize = 11.sp)
        if (result.players.isEmpty()) {
            Text(result.message.ifBlank { "没有找到匹配的玩家" }, color = CokPalette.warn, fontSize = 12.sp)
        } else {
            if (result.stale) {
                Text("坐标可能已过期，建议重新全图扫描", color = CokPalette.warn, fontSize = 11.sp)
            }
            result.players.forEach { player ->
                val detail = buildString {
                    append("X ${player.x} · Y ${player.y}")
                    if (player.level.isNotBlank()) append(" · 等级 ${player.level}")
                }
                Text(player.name.ifBlank { player.uid }, color = CokPalette.fg, fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
                Text(detail, color = CokPalette.accentText, fontSize = 12.sp)
            }
        }
    }
}

@Composable
private fun MoreSection(text: String) = Text(text.uppercase(), color = CokPalette.dim2, fontSize = 11.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.1.sp)

@Composable
private fun MoreRow(title: String, detail: String, onClick: () -> Unit) = Row(
    Modifier.fillMaxWidth().clip(RoundedCornerShape(10.dp)).background(CokPalette.surface).border(1.dp, CokPalette.line, RoundedCornerShape(10.dp)).clickable(onClick = onClick).padding(14.dp),
    verticalAlignment = Alignment.CenterVertically,
) {
    Column(Modifier.weight(1f)) {
        Text(title, color = CokPalette.fg, fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
        Spacer(Modifier.height(3.dp))
        Text(detail, color = CokPalette.dim, fontSize = 12.sp)
    }
    Text(">", color = CokPalette.dim2, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
}

@Composable
private fun EventRow(event: ConsoleEvent) = Row(
    Modifier.fillMaxWidth().clip(RoundedCornerShape(8.dp)).background(CokPalette.surface).border(1.dp, CokPalette.line, RoundedCornerShape(8.dp)).padding(12.dp),
    verticalAlignment = Alignment.Top,
) {
    Box(Modifier.padding(top = 5.dp).height(8.dp).width(8.dp).clip(RoundedCornerShape(4.dp)).background(severityColor(event.severity)))
    Spacer(Modifier.width(10.dp))
    Column(Modifier.weight(1f)) {
        Text(event.message, color = CokPalette.fg, fontSize = 13.sp)
        if (event.time.isNotBlank()) { Spacer(Modifier.height(3.dp)); Text(event.time, color = CokPalette.dim2, fontSize = 11.sp) }
    }
}

@Composable
private fun EmptyEvents() = Box(Modifier.fillMaxWidth().clip(RoundedCornerShape(8.dp)).background(CokPalette.surface).border(1.dp, CokPalette.line, RoundedCornerShape(8.dp)).padding(16.dp)) {
    Text("还没有可展示的运行记录", color = CokPalette.dim, fontSize = 13.sp)
}
