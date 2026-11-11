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
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Checkbox
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.Refresh

/** Native account centre. */
@Composable
fun AccountScreen(
    ui: HomeUiState,
    onRefresh: () -> Unit,
    onSwitch: (String) -> Unit,
    onSetParallel: (String, Boolean) -> Unit,
    onSetAccountsParallel: (List<String>, Boolean) -> Unit,
    onSetPriority: (String, Int) -> Unit,
    onImport: () -> Unit,
    onRename: (String, String) -> Unit,
    onRemove: (String) -> Unit,
    onChannelLogin: (String, String) -> Unit,
    onChannelAdd: (String, List<String>) -> Unit,
    onClearChannelLogin: () -> Unit,
) {
    val snapshot = ui.snapshot
    val accounts = snapshot?.accounts.orEmpty()
    val accountKeys = accounts.map { it.key }
    var renameTarget by remember { mutableStateOf<AccountProfile?>(null) }
    var removeTarget by remember { mutableStateOf<AccountProfile?>(null) }
    var channelLoginOpen by remember { mutableStateOf(false) }

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp, 12.dp, 16.dp, 28.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.weight(1f)) {
                    Text("账号管理", color = CokPalette.fg, fontSize = 22.sp, fontWeight = FontWeight.Bold)
                    Spacer(Modifier.height(6.dp))
                    Text("切换当前账号，管理后台运行与本机导入", color = CokPalette.dim, fontSize = 13.sp)
                }
                IconButton(onClick = onRefresh, enabled = !ui.refreshing) {
                    Icon(Icons.Filled.Refresh, contentDescription = "刷新账号状态", tint = CokPalette.accentText)
                }
            }
        }
        item {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                OutlinedButton(
                    onClick = onImport,
                    enabled = !ui.refreshing && !ui.accountActionInFlight,
                    modifier = Modifier.weight(1f),
                    shape = RoundedCornerShape(8.dp),
                ) {
                    Text("本机导入", color = CokPalette.accentText)
                }
                Button(
                    onClick = {
                        onClearChannelLogin()
                        channelLoginOpen = true
                    },
                    enabled = !ui.refreshing && !ui.accountActionInFlight,
                    modifier = Modifier.weight(1f),
                    shape = RoundedCornerShape(8.dp),
                ) {
                    Text("果盘账号登录", fontSize = 13.sp)
                }
            }
        }
        if (accounts.isNotEmpty()) {
            item {
                AccountOperationsSummary(
                    accounts = accounts,
                    busy = ui.refreshing || ui.accountActionInFlight,
                    onSetAllParallel = { enabled -> onSetAccountsParallel(accountKeys, enabled) },
                )
            }
        }
        item { AccountSectionLabel("账号库 · ${snapshot?.accounts?.size ?: 0}") }
        if (accounts.isEmpty()) {
            item { EmptyAccounts() }
        } else {
            items(accounts, key = { it.key }) { account ->
                AccountRow(
                    account = account,
                    accountSource = if (account.isActive) snapshot?.accountSource.orEmpty() else "",
                    actionBusy = ui.refreshing || ui.accountActionInFlight,
                    onSwitch = { onSwitch(account.key) },
                    onSetParallel = { onSetParallel(account.key, it) },
                    onSetPriority = { onSetPriority(account.key, it) },
                    onRename = { renameTarget = account },
                    onRemove = { removeTarget = account },
                )
            }
        }
    }

    if (channelLoginOpen) {
        ChannelLoginDialog(
            ui = ui,
            onDismiss = {
                onClearChannelLogin()
                channelLoginOpen = false
            },
            onLogin = onChannelLogin,
            onAdd = onChannelAdd,
        )
    }

    renameTarget?.let { account ->
        RenameAccountDialog(
            account = account,
            onDismiss = { renameTarget = null },
            onConfirm = { label -> onRename(account.key, label); renameTarget = null },
        )
    }
    removeTarget?.let { account ->
        AlertDialog(
            onDismissRequest = { removeTarget = null },
            title = { Text("移除账号") },
            text = { Text("从账号库移除“${account.label}”？已扫描的数据不会删除。") },
            confirmButton = {
                Button(
                    onClick = { onRemove(account.key); removeTarget = null },
                    colors = ButtonDefaults.buttonColors(containerColor = CokPalette.err),
                ) { Text("移除") }
            },
            dismissButton = { OutlinedButton(onClick = { removeTarget = null }) { Text("取消") } },
        )
    }
}

@Composable
private fun ChannelLoginDialog(
    ui: HomeUiState,
    onDismiss: () -> Unit,
    onLogin: (String, String) -> Unit,
    onAdd: (String, List<String>) -> Unit,
) {
    var account by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    val result = ui.channelLoginResult
    var selectedIds by remember(result?.sessionId) { mutableStateOf(emptySet<String>()) }
    val selectable = result?.smallAccounts.orEmpty().filter { it.hasCharacter && !it.inLibrary }
    val scrollState = rememberScrollState()

    AlertDialog(
        onDismissRequest = { if (!ui.channelLoginInFlight && !ui.channelAddInFlight) onDismiss() },
        title = { Text(if (result == null) "果盘账号登录" else "选择游戏账号") },
        text = {
            Column(
                modifier = Modifier.heightIn(max = 480.dp).verticalScroll(scrollState),
                verticalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                if (result == null) {
                    Text("登录后可选择该果盘账号下的游戏角色加入账号库。", color = CokPalette.dim, fontSize = 13.sp)
                    OutlinedTextField(
                        value = account,
                        onValueChange = { account = it },
                        enabled = !ui.channelLoginInFlight,
                        singleLine = true,
                        label = { Text("果盘账号") },
                        modifier = Modifier.fillMaxWidth(),
                    )
                    OutlinedTextField(
                        value = password,
                        onValueChange = { password = it },
                        enabled = !ui.channelLoginInFlight,
                        singleLine = true,
                        label = { Text("密码") },
                        visualTransformation = PasswordVisualTransformation(),
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                        modifier = Modifier.fillMaxWidth(),
                    )
                } else {
                    Text(
                        buildString {
                            append("已登录 ").append(result.account)
                            if (result.guopanUid.isNotBlank()) append(" · UID ").append(result.guopanUid)
                        },
                        color = CokPalette.fg,
                        fontSize = 13.sp,
                        fontWeight = FontWeight.SemiBold,
                    )
                    if (result.note.isNotBlank()) Text(result.note, color = CokPalette.dim, fontSize = 12.sp)
                    if (result.smallAccounts.isEmpty()) {
                        Text("该果盘账号尚未发现可用游戏角色。", color = CokPalette.dim, fontSize = 13.sp)
                    } else {
                        if (selectable.isNotEmpty()) {
                            OutlinedButton(
                                onClick = { selectedIds = selectable.map { it.perGameId }.toSet() },
                                enabled = !ui.channelAddInFlight,
                                shape = RoundedCornerShape(7.dp),
                            ) { Text("全选可添加账号", fontSize = 12.sp) }
                        }
                        result.smallAccounts.forEach { gameAccount ->
                            ChannelAccountRow(
                                account = gameAccount,
                                checked = gameAccount.perGameId in selectedIds,
                                enabled = gameAccount.hasCharacter && !gameAccount.inLibrary && !ui.channelAddInFlight,
                                onCheckedChange = { checked ->
                                    selectedIds = if (checked) selectedIds + gameAccount.perGameId else selectedIds - gameAccount.perGameId
                                },
                            )
                        }
                    }
                }
                ui.channelLoginError?.let { Text(it, color = CokPalette.err, fontSize = 12.sp, lineHeight = 17.sp) }
            }
        },
        confirmButton = {
            if (result == null) {
                Button(
                    onClick = {
                        onLogin(account, password)
                        password = ""
                    },
                    enabled = account.isNotBlank() && password.isNotBlank() && !ui.channelLoginInFlight,
                ) {
                    if (ui.channelLoginInFlight) {
                        CircularProgressIndicator(modifier = Modifier.height(18.dp).width(18.dp), strokeWidth = 2.dp, color = CokPalette.fg)
                    } else Text("登录")
                }
            } else {
                Button(
                    onClick = { onAdd(result.sessionId, selectedIds.toList()) },
                    enabled = selectedIds.isNotEmpty() && !ui.channelAddInFlight,
                ) {
                    if (ui.channelAddInFlight) {
                        CircularProgressIndicator(modifier = Modifier.height(18.dp).width(18.dp), strokeWidth = 2.dp, color = CokPalette.fg)
                    } else Text("加入账号库 (${selectedIds.size})")
                }
            }
        },
        dismissButton = {
            OutlinedButton(onClick = onDismiss, enabled = !ui.channelLoginInFlight && !ui.channelAddInFlight) {
                Text(if (result == null) "取消" else "完成")
            }
        },
    )
}

@Composable
private fun ChannelAccountRow(
    account: ChannelGameAccount,
    checked: Boolean,
    enabled: Boolean,
    onCheckedChange: (Boolean) -> Unit,
) {
    val status = when {
        account.inLibrary -> "已加入"
        !account.hasCharacter -> "未创建角色"
        else -> "可添加"
    }
    Column(
        Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(7.dp))
            .background(CokPalette.surfaceHigher)
            .clickable(enabled = enabled) { onCheckedChange(!checked) }
            .padding(10.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Checkbox(checked = checked, onCheckedChange = onCheckedChange, enabled = enabled)
            Spacer(Modifier.width(4.dp))
            Column(Modifier.weight(1f)) {
                Text(account.roleName.ifBlank { account.name.ifBlank { "未命名角色" } }, color = if (enabled) CokPalette.fg else CokPalette.dim, fontSize = 14.sp, fontWeight = FontWeight.SemiBold)
                val details = listOfNotNull(
                    account.gameUid.takeIf { it.isNotBlank() }?.let { "UID $it" },
                    account.zone.takeIf { it.isNotBlank() }?.let { "区服 $it" },
                    account.level.takeIf { it.isNotBlank() }?.let { "等级 $it" },
                )
                if (details.isNotEmpty()) Text(details.joinToString(" · "), color = CokPalette.dim2, fontSize = 11.sp)
            }
            Text(status, color = if (enabled) CokPalette.accentText else CokPalette.dim2, fontSize = 11.sp)
        }
        if (!account.hasCharacter && account.note.isNotBlank()) {
            Text(account.note, color = CokPalette.dim2, fontSize = 11.sp, modifier = Modifier.padding(start = 52.dp, top = 2.dp))
        }
    }
}

@Composable
private fun AccountOperationsSummary(
    accounts: List<AccountProfile>,
    busy: Boolean,
    onSetAllParallel: (Boolean) -> Unit,
) {
    val managed = accounts.count { it.isParallel }
    val automated = accounts.count { it.automationEnabled > 0 && !it.automationPaused }
    val paused = accounts.count { it.automationPaused }
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        AccountSectionLabel("运营概览")
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            AccountMetric("账号", accounts.size.toString())
            AccountMetric("后台", managed.toString())
            AccountMetric("已启用规则", automated.toString())
            AccountMetric("已暂停", paused.toString())
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
            Button(
                onClick = { onSetAllParallel(true) },
                enabled = !busy && managed < accounts.size,
                modifier = Modifier.weight(1f),
                shape = RoundedCornerShape(7.dp),
            ) { Text("全部后台托管", fontSize = 12.sp) }
            OutlinedButton(
                onClick = { onSetAllParallel(false) },
                enabled = !busy && managed > 0,
                modifier = Modifier.weight(1f),
                shape = RoundedCornerShape(7.dp),
            ) { Text("停止全部后台", color = CokPalette.dim, fontSize = 12.sp) }
        }
    }
}

@Composable
private fun AccountMetric(label: String, value: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(value, color = CokPalette.fg, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
        Text(label, color = CokPalette.dim2, fontSize = 10.sp, maxLines = 1)
    }
}

@Composable
private fun AccountRow(
    account: AccountProfile,
    accountSource: String,
    actionBusy: Boolean,
    onSwitch: () -> Unit,
    onSetParallel: (Boolean) -> Unit,
    onSetPriority: (Int) -> Unit,
    onRename: () -> Unit,
    onRemove: () -> Unit,
) {
    var menuExpanded by remember(account.key) { mutableStateOf(false) }
    Column(
        Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .background(if (account.isActive) CokPalette.surfaceHigh else CokPalette.surface)
            .border(1.dp, if (account.isActive) CokPalette.accent.copy(alpha = .7f) else CokPalette.line, RoundedCornerShape(10.dp))
            .clickable(enabled = !account.isActive && !actionBusy, onClick = onSwitch)
            .padding(14.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(account.label, color = CokPalette.fg, fontSize = 16.sp, fontWeight = FontWeight.SemiBold, maxLines = 1, overflow = TextOverflow.Ellipsis)
                    if (account.isActive) {
                        Spacer(Modifier.width(8.dp))
                        Text("当前", color = CokPalette.accentText, fontSize = 11.sp)
                    }
                }
                val details = listOfNotNull(
                    account.roleName.takeIf { it.isNotBlank() },
                    account.gameUid.takeIf { it.isNotBlank() }?.let { "UID $it" },
                    account.server.takeIf { it.isNotBlank() },
                )
                if (details.isNotEmpty()) {
                    Spacer(Modifier.height(4.dp))
                    Text(details.joinToString(" · "), color = CokPalette.dim2, fontSize = 12.sp, maxLines = 2, overflow = TextOverflow.Ellipsis)
                }
                if (accountSource.isNotBlank()) {
                    Spacer(Modifier.height(4.dp))
                    Text(accountSource, color = CokPalette.dim, fontSize = 11.sp, maxLines = 1, overflow = TextOverflow.Ellipsis)
                }
                val fleet = account.summary
                if (account.isRunning && fleet != null) {
                    Spacer(Modifier.height(5.dp))
                    val parts = buildList {
                        when {
                            fleet.error.isNotBlank() -> add("异常" to CokPalette.err)
                            fleet.disconnected -> add("已断开" to CokPalette.dim)
                            fleet.stale -> add("久无响应" to CokPalette.warn)
                        }
                        if (fleet.hunting) add(("打怪" + if (fleet.huntKills > 0) " ${fleet.huntKills}" else "") to CokPalette.ok)
                        if (fleet.hasShield) add("有罩" to CokPalette.ok) else add("无罩" to CokPalette.warn)
                        if (fleet.dockRewardable > 0) add("港口待领 ${fleet.dockRewardable}" to CokPalette.warn)
                        if (fleet.welfareClaimable) add("好礼待领" to CokPalette.warn)
                        if (fleet.appYield) add("让号中" to CokPalette.dim)
                    }
                    Text(
                        parts.joinToString(" · ") { it.first },
                        color = parts.firstOrNull { it.second == CokPalette.err }?.second
                            ?: parts.firstOrNull { it.second == CokPalette.warn }?.second
                            ?: CokPalette.ok,
                        fontSize = 11.sp,
                        maxLines = 2,
                        overflow = TextOverflow.Ellipsis,
                    )
                    if (fleet.error.isNotBlank()) {
                        Text(fleet.error.take(80), color = CokPalette.err, fontSize = 11.sp, maxLines = 2, overflow = TextOverflow.Ellipsis)
                    }
                }
            }
            if (!account.isActive) {
                OutlinedButton(onClick = onSwitch, enabled = !actionBusy, shape = RoundedCornerShape(8.dp)) {
                    Text("切换", color = CokPalette.accentText, fontSize = 12.sp)
                }
            }
            Box {
                IconButton(onClick = { menuExpanded = true }, enabled = !actionBusy) {
                    Icon(Icons.Filled.MoreVert, contentDescription = "账号更多操作", tint = CokPalette.dim)
                }
                DropdownMenu(expanded = menuExpanded, onDismissRequest = { menuExpanded = false }) {
                    DropdownMenuItem(
                        text = { Text("修改名称") },
                        onClick = { menuExpanded = false; onRename() },
                    )
                    DropdownMenuItem(
                        text = { Text("移除账号", color = CokPalette.err) },
                        onClick = { menuExpanded = false; onRemove() },
                    )
                }
            }
        }
        Spacer(Modifier.height(12.dp))
        Column(
            Modifier.fillMaxWidth().clip(RoundedCornerShape(7.dp)).background(CokPalette.surfaceHigher).padding(10.dp),
        ) {
            Text("自动化托管", color = CokPalette.dim2, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
            Text(
                when {
                    account.automationPaused -> "已暂停全部自动化"
                    account.automationEnabled > 0 -> "已启用 ${account.automationEnabled} 项规则 · ${account.lastAutomationSummary}"
                    else -> "尚未启用自动处理规则"
                },
                color = if (account.automationPaused) CokPalette.warn else CokPalette.dim,
                fontSize = 11.sp,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis,
            )
        }
        Spacer(Modifier.height(10.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text("调度优先级", color = CokPalette.fg, fontSize = 13.sp)
                Text("后台账号启动和巡检顺序", color = CokPalette.dim2, fontSize = 11.sp)
            }
            Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                (1..3).forEach { priority ->
                    OutlinedButton(
                        onClick = { onSetPriority(priority) },
                        enabled = !actionBusy,
                        contentPadding = PaddingValues(horizontal = 9.dp, vertical = 0.dp),
                        shape = RoundedCornerShape(6.dp),
                        colors = ButtonDefaults.outlinedButtonColors(
                            containerColor = if (account.priority == priority) CokPalette.accent.copy(alpha = .14f) else Color.Transparent,
                        ),
                    ) { Text(priority.toString(), color = if (account.priority == priority) CokPalette.accentText else CokPalette.dim, fontSize = 11.sp) }
                }
            }
        }
        Spacer(Modifier.height(10.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text("后台运行", color = CokPalette.fg, fontSize = 13.sp)
                Text(if (account.isParallel) "持续轮询与守护已开启" else "仅在当前查看时运行", color = CokPalette.dim2, fontSize = 11.sp)
            }
            Switch(checked = account.isParallel, onCheckedChange = onSetParallel, enabled = !actionBusy)
        }
    }
}

@Composable
private fun RenameAccountDialog(account: AccountProfile, onDismiss: () -> Unit, onConfirm: (String) -> Unit) {
    var label by remember(account.key) { mutableStateOf(account.label) }
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("修改账号名称") },
        text = {
            OutlinedTextField(value = label, onValueChange = { label = it }, singleLine = true, label = { Text("账号名称") })
        },
        confirmButton = {
            Button(onClick = { onConfirm(label.trim()) }, enabled = label.isNotBlank()) { Text("保存") }
        },
        dismissButton = { OutlinedButton(onClick = onDismiss) { Text("取消") } },
    )
}

@Composable
private fun AccountSectionLabel(text: String) {
    Text(text.uppercase(), color = CokPalette.dim2, fontSize = 11.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.1.sp)
}

@Composable
private fun EmptyAccounts() {
    Box(
        Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .background(CokPalette.surface)
            .border(1.dp, CokPalette.line, RoundedCornerShape(10.dp))
            .padding(18.dp),
    ) {
        Text("尚未登记账号。可从本机已安装的游戏包中导入。", color = CokPalette.dim, fontSize = 13.sp)
    }
}
