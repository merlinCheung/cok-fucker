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
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.filled.KeyboardArrowUp
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.input.pointer.PointerEventPass
import androidx.compose.ui.input.pointer.changedToDown
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.TextRange
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.TextFieldValue
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

private sealed interface ConfirmOperation {
    data class DailyAction(val action: QuickAction) : ConfirmOperation
    data class UseShield(val slot: ShieldSlot, val item: ShieldItem) : ConfirmOperation
    data object StartHunt : ConfirmOperation
    data object StartExplore : ConfirmOperation
    data object StartRally : ConfirmOperation
    data class ItemSpeedup(val queue: QueueStatus, val item: SpeedupItem, val count: Int) : ConfirmOperation
    data class GoldSpeedup(val queue: QueueStatus) : ConfirmOperation
}

/** The mobile first path: daily actions, safety, and recurring automation. */
@Composable
fun OperationsScreen(
    ui: HomeUiState,
    backgroundMonitoringEnabled: Boolean,
    initialFocus: OperationsFocus?,
    onFocusHandled: () -> Unit,
    onAction: (QuickAction) -> Unit,
    onSetAutomation: (String, Boolean, String) -> Unit,
    onSaveAutomationPolicy: (Boolean, String, Int, Int, String, Int, Int, Int) -> Unit,
    onRecheckAutomation: (String) -> Unit,
    onSaveHuntPlan: (Int, Int, Int, Int, Int, Boolean) -> Unit,
    onUseShield: (ShieldSlot, ShieldItem) -> Unit,
    onStartHunt: (Int, Int, Int, Int, Int, Boolean) -> Unit,
    onStopHunt: () -> Unit,
    onSpeedUpWithItem: (QueueStatus, SpeedupItem, Int) -> Unit,
    onSpeedUpWithGold: (QueueStatus) -> Unit,
    onClaimSkyReward: () -> Unit,
    onStartSkyExplore: () -> Unit,
    onLoadRally: (Boolean) -> Unit,
    onStartRally: (Int, Int, Int) -> Unit,
    onOpenConsole: () -> Unit,
) {
    val snapshot = ui.snapshot
    val operations = snapshot?.operations
    val dataAvailable = snapshot?.gameDataAvailable == true
    val operationBusy = ui.operationInFlight ?: ui.actionInFlight?.name ?: if (dataAvailable) null else "data-unavailable"
    val listState = rememberLazyListState()
    var confirm by remember { mutableStateOf<ConfirmOperation?>(null) }
    var huntLevel by remember(operations?.hunt?.level) { mutableIntStateOf(operations?.hunt?.level ?: 1) }
    var huntSquads by remember(operations?.hunt?.squadCount) { mutableIntStateOf(operations?.hunt?.squadCount ?: 4) }
    var huntSoldiers by remember(operations?.hunt?.soldiersPerSquad) { mutableIntStateOf(operations?.hunt?.soldiersPerSquad ?: 5_000) }
    var huntMaxKills by remember(operations?.hunt?.maxKills) { mutableIntStateOf(operations?.hunt?.maxKills ?: 0) }
    var huntMix by remember(operations?.hunt?.mix) { mutableIntStateOf(operations?.hunt?.mix ?: 1) }
    var huntAutoStamina by remember(operations?.hunt?.autoStamina) { mutableStateOf(operations?.hunt?.autoStamina ?: false) }
    var costlyAssist by remember { mutableStateOf(false) }
    var rallyLevel by remember { mutableIntStateOf(0) }
    var rallyTarget by remember { mutableIntStateOf(0) }
    var rallySlot by remember { mutableIntStateOf(1) }
    var rallySoldiers by remember { mutableIntStateOf(2_000) }

    // 集结状态要发 world.get 拉地块, 比主轮询慢得多 —— 只在进操作页时读一次,
    // 之后靠「刷新」按钮手动更新, 不跟主轮询抢账号连接。
    LaunchedEffect(Unit) {
        if (ui.rally == null) onLoadRally(false)
    }
    // 选中的目标必须还在当前等级里, 否则自动挑一只没有集结的
    val rallyBosses = remember(ui.rally, rallyLevel) {
        val all = ui.rally?.bosses.orEmpty()
        if (rallyLevel == 0) all else all.filter { it.level == rallyLevel }
    }
    LaunchedEffect(rallyBosses) {
        val stillThere = rallyBosses.any { it.index == rallyTarget }
        if (!stillThere) {
            rallyTarget = rallyBosses.firstOrNull { !it.busy }?.index
                ?: rallyBosses.firstOrNull()?.index ?: 0
        }
    }

    LaunchedEffect(initialFocus) {
        val target = when (initialFocus) {
            OperationsFocus.SAFETY -> SAFETY_SECTION_INDEX
            OperationsFocus.HUNT -> HUNT_SECTION_INDEX
            null -> null
        }
        if (target != null) {
            listState.scrollToItem(target)
            onFocusHandled()
        }
    }

    LazyColumn(
        state = listState,
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp, 12.dp, 16.dp, 28.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item {
            Text("操作", color = CokPalette.fg, fontSize = 22.sp, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(6.dp))
            Text(snapshot?.account?.let { "当前账号 · $it" } ?: "正在读取当前账号", color = CokPalette.dim, fontSize = 13.sp)
        }
        ui.actionOutcome?.let { outcome ->
            item { ActionOutcomeCard(outcome) }
        }
        item { OperationSection("今日处理") }
        item {
            DailyActions(ui.actionInFlight, operationBusy != null) { action ->
                if (action.requiresConfirm) confirm = ConfirmOperation.DailyAction(action) else onAction(action)
            }
        }
        item { OperationSection("自动处理") }
        item {
            AutomationCentre(
                settings = operations?.automation,
                runtime = operations?.automationRuntime,
                rules = operations?.automationRules.orEmpty(),
                history = operations?.automationHistory.orEmpty(),
                alerts = operations?.automationAlerts.orEmpty(),
                policy = operations?.automationPolicy,
                backgroundMonitoringEnabled = backgroundMonitoringEnabled,
                updatingKey = ui.automationSettingInFlight,
                operationInFlight = ui.operationInFlight,
                onSetAutomation = onSetAutomation,
                onSavePolicy = onSaveAutomationPolicy,
                onRecheck = onRecheckAutomation,
            )
        }
        if (!dataAvailable) {
            item {
                DataUnavailableCard()
            }
        } else {
            item { OperationSection("安全与队列") }
            item {
                SafetyCard(
                    operations = operations,
                    busy = operationBusy,
                    onUseShield = { slot, item -> confirm = ConfirmOperation.UseShield(slot, item) },
                )
            }
            item {
                QueueSpeedupCard(
                    queues = operations?.runningQueues.orEmpty(),
                    items = operations?.speedupItems.orEmpty(),
                    busy = operationBusy,
                    onUseItem = { queue, item, count -> confirm = ConfirmOperation.ItemSpeedup(queue, item, count) },
                    onUseGold = { queue -> confirm = ConfirmOperation.GoldSpeedup(queue) },
                )
            }
            item { OperationSection("港口贸易") }
            item {
                DockCard(
                    dock = operations?.dock,
                    busy = operationBusy,
                    onClaim = { confirm = ConfirmOperation.DailyAction(QuickAction.DOCK_REWARD) },
                )
            }
            item { OperationSection("打怪与探索") }
            item {
                HuntCard(
                    hunt = operations?.hunt,
                    dataAvailable = operations?.huntDataAvailable == true,
                    unavailableReason = operations?.huntUnavailableReason.orEmpty(),
                    level = huntLevel,
                    squads = huntSquads,
                    soldiersPerSquad = huntSoldiers,
                    maxKills = huntMaxKills,
                    mix = huntMix,
                    autoStamina = huntAutoStamina,
                    busy = operationBusy,
                    onLevelChange = { huntLevel = it },
                    onSquadsChange = { huntSquads = it },
                    onSoldiersChange = { huntSoldiers = it },
                    onMaxKillsChange = { huntMaxKills = it },
                    onMixChange = { huntMix = it },
                    onAutoStaminaChange = { huntAutoStamina = it },
                    saving = ui.automationSettingInFlight == "hunt-plan",
                    onSavePlan = {
                        onSaveHuntPlan(huntLevel, huntSoldiers, huntSquads, huntMaxKills, huntMix, huntAutoStamina)
                    },
                    onStart = { confirm = ConfirmOperation.StartHunt },
                    onStop = onStopHunt,
                )
            }
            item {
                RallyCard(
                    rally = ui.rally,
                    loading = ui.rallyInFlight,
                    busy = ui.operationInFlight,
                    level = rallyLevel,
                    onLevelChange = { rallyLevel = it },
                    target = rallyTarget,
                    onTargetChange = { rallyTarget = it },
                    slot = rallySlot,
                    onSlotChange = { rallySlot = it },
                    soldiers = rallySoldiers,
                    onSoldiersChange = { rallySoldiers = it },
                    onRefresh = { onLoadRally(true) },
                    onStart = { confirm = ConfirmOperation.StartRally },
                )
            }
            item {
                SkyCard(
                    sky = operations?.sky,
                    busy = operationBusy,
                    onClaim = onClaimSkyReward,
                    onExplore = { confirm = ConfirmOperation.StartExplore },
                )
            }
        }
        item { OperationSection("联盟") }
        item {
            AllianceCard(
                alliance = operations?.alliance,
                busy = operationBusy,
                onAccept = { confirm = ConfirmOperation.DailyAction(QuickAction.ALLIANCE_ACCEPT) },
                onDonate = { confirm = ConfirmOperation.DailyAction(QuickAction.ALLIANCE_DONATE) },
                onHelpAll = { confirm = ConfirmOperation.DailyAction(QuickAction.ALLIANCE_HELP_ALL) },
                onSignIn = { confirm = ConfirmOperation.DailyAction(QuickAction.ALLIANCE_SIGN_IN) },
            )
        }
        item { OperationSection("一键完成") }
        item {
            QuickAssistCard(
                assist = operations?.assist,
                busy = operationBusy,
                costly = costlyAssist,
                onCostlyChange = { costlyAssist = it },
                onRun = { confirm = ConfirmOperation.DailyAction(QuickAction.ASSIST) },
            )
        }
        item { OperationSection("完整控制台") }
        item { AdvancedConsoleCard(onOpenConsole) }
    }

    val confirmOperation = confirm
    when (confirmOperation) {
        is ConfirmOperation.DailyAction -> QuickActionConfirmation(
            action = confirmOperation.action,
            onDismiss = { confirm = null },
            onConfirm = { onAction(confirmOperation.action); confirm = null },
        )
        is ConfirmOperation.UseShield -> ConfirmDialog(
            title = "确认开启保护罩",
            body = shieldConfirmation(confirmOperation.slot, confirmOperation.item),
            confirmLabel = "消耗道具并开启",
            danger = true,
            onDismiss = { confirm = null },
            onConfirm = { onUseShield(confirmOperation.slot, confirmOperation.item); confirm = null },
        )
        ConfirmOperation.StartHunt -> ConfirmDialog(
            title = "开始自动打怪",
            body = huntConfirmation(
                level = huntLevel,
                squads = huntSquads,
                soldiersPerSquad = huntSoldiers,
                maxKills = huntMaxKills,
                mix = huntMix,
                autoStamina = huntAutoStamina,
            ),
            confirmLabel = "开始打怪",
            onDismiss = { confirm = null },
            onConfirm = {
                onStartHunt(huntLevel, huntSoldiers, huntSquads, huntMaxKills, huntMix, huntAutoStamina)
                confirm = null
            },
        )
        ConfirmOperation.StartRally -> ConfirmDialog(
            title = "发起联盟集结",
            body = rallyConfirmation(
                target = rallyBosses.firstOrNull { it.index == rallyTarget },
                minutes = ui.rally?.slots?.firstOrNull { it.slot == rallySlot }?.minutes ?: rallySlot,
                soldiers = rallySoldiers,
                staminaCost = ui.rally?.staminaCost ?: 20,
            ),
            confirmLabel = "发起集结",
            danger = true,
            onDismiss = { confirm = null },
            onConfirm = { onStartRally(rallyTarget, rallySlot, rallySoldiers); confirm = null },
        )
        ConfirmOperation.StartExplore -> ConfirmDialog(
            title = "开始探索",
            body = "将开始一次探索。探索会按游戏规则消耗战力或部队。",
            confirmLabel = "确认探索",
            onDismiss = { confirm = null },
            onConfirm = { onStartSkyExplore(); confirm = null },
        )
        is ConfirmOperation.ItemSpeedup -> ConfirmDialog(
            title = "确认使用道具加速",
            body = speedupConfirmation(confirmOperation.queue, confirmOperation.item, confirmOperation.count),
            confirmLabel = "使用道具",
            onDismiss = { confirm = null },
            onConfirm = { onSpeedUpWithItem(confirmOperation.queue, confirmOperation.item, confirmOperation.count); confirm = null },
        )
        is ConfirmOperation.GoldSpeedup -> ConfirmDialog(
            title = "确认金币加速",
            body = "将使用金币加速“${confirmOperation.queue.name} · ${confirmOperation.queue.detail}”。游戏会按当前剩余时间计算实际金币消耗，提交后会立即扣除金币。",
            confirmLabel = "确认用金币",
            danger = true,
            onDismiss = { confirm = null },
            onConfirm = { onSpeedUpWithGold(confirmOperation.queue); confirm = null },
        )
        null -> Unit
    }
}

@Composable
private fun DataUnavailableCard() {
    Column(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(10.dp))
            .background(CokPalette.surface)
            .border(1.dp, CokPalette.line, RoundedCornerShape(10.dp))
            .padding(14.dp),
    ) {
        Text("正在读取游戏状态", color = CokPalette.fg, fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
        Spacer(Modifier.height(5.dp))
        Text(
            "安全、队列与打怪数据尚未同步。涉及账号的操作暂不可用；请稍候，或返回状态页刷新。",
            color = CokPalette.dim,
            fontSize = 12.sp,
            lineHeight = 17.sp,
        )
    }
}

private enum class AutomationView(val label: String) { RULES("规则"), TASKS("任务"), HISTORY("历史"), POLICY("策略") }

@Composable
private fun AutomationCentre(
    settings: AutomationSettings?,
    runtime: AutomationRuntime?,
    rules: List<AutomationRule>,
    history: List<AutomationHistoryItem>,
    alerts: List<AutomationAlert>,
    policy: AutomationPolicy?,
    backgroundMonitoringEnabled: Boolean,
    updatingKey: String?,
    operationInFlight: String?,
    onSetAutomation: (String, Boolean, String) -> Unit,
    onSavePolicy: (Boolean, String, Int, Int, String, Int, Int, Int) -> Unit,
    onRecheck: (String) -> Unit,
) {
    var view by rememberSaveable { mutableStateOf(AutomationView.RULES) }
    Column(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(10.dp))
            .background(CokPalette.surface)
            .border(1.dp, CokPalette.line, RoundedCornerShape(10.dp))
            .padding(14.dp),
        verticalArrangement = Arrangement.spacedBy(2.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text("自动处理规则", color = CokPalette.fg, fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
                Text(
                    if (settings == null) "正在读取已保存的规则"
                    else "已启用 ${settings.enabledCount} 项 · 下次刷新时生效",
                    color = CokPalette.dim,
                    fontSize = 12.sp,
                )
            }
        }
        Spacer(Modifier.height(7.dp))
        AutomationRuntimeSummary(runtime, settings, backgroundMonitoringEnabled)
        Spacer(Modifier.height(8.dp))
        AutomationTabs(selected = view, onSelect = { view = it })
        Spacer(Modifier.height(8.dp))
        when (view) {
            AutomationView.RULES -> AutomationRules(settings, updatingKey, onSetAutomation)
            AutomationView.TASKS -> AutomationTaskList(rules, alerts, operationInFlight, onRecheck)
            AutomationView.HISTORY -> AutomationHistoryList(history)
            AutomationView.POLICY -> AutomationPolicyPanel(policy, updatingKey == "automation-policy", onSavePolicy)
        }
    }
}

@Composable
private fun AutomationRules(
    settings: AutomationSettings?,
    updatingKey: String?,
    onSetAutomation: (String, Boolean, String) -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
        AutomationToggle(
            title = "自动签到",
            detail = "每天检测到可签到时自动完成",
            settingKey = "autoSign",
            enabled = settings?.autoSign == true,
            updatingKey = updatingKey,
            onSetAutomation = onSetAutomation,
        )
        AutomationToggle(
            title = "被攻击自动保护",
            detail = "收到攻击推送时使用已配置的保护罩",
            settingKey = "autoShield",
            enabled = settings?.autoShield == true,
            updatingKey = updatingKey,
            onSetAutomation = onSetAutomation,
        )
        AutomationToggle(
            title = "自动领取福利",
            detail = "每日好礼、龙之馈赠可领取时处理",
            settingKey = "autoWelfare",
            enabled = settings?.autoWelfare == true,
            updatingKey = updatingKey,
            onSetAutomation = onSetAutomation,
        )
        AutomationToggle(
            title = "自动领取积分任务",
            detail = "积分商城任务奖励可领取时处理",
            settingKey = "scoreAutoClaim",
            enabled = settings?.scoreAutoClaim == true,
            updatingKey = updatingKey,
            onSetAutomation = onSetAutomation,
        )
        AutomationToggle(
            title = "港口自动领取",
            detail = "贸易完成并可领取时自动领取",
            settingKey = "dockAutoReward",
            enabled = settings?.dockAutoReward == true,
            updatingKey = updatingKey,
            onSetAutomation = onSetAutomation,
        )
        AutomationToggle(
            title = "港口自动分派",
            detail = "空闲船位会按控制台配置自动分派",
            settingKey = "dockAutoSend",
            enabled = settings?.dockAutoSend == true,
            updatingKey = updatingKey,
            onSetAutomation = onSetAutomation,
        )
        AutomationToggle(
            title = "天空之境自动领奖",
            detail = "探索完成后自动领取奖励",
            settingKey = "skyAutoReward",
            enabled = settings?.skyAutoReward == true,
            updatingKey = updatingKey,
            onSetAutomation = onSetAutomation,
        )
        AutomationToggle(
            title = "天空之境自动探索",
            detail = "空闲时继续探索，会按游戏规则消耗战力或部队",
            settingKey = "skyAutoExplore",
            enabled = settings?.skyAutoExplore == true,
            updatingKey = updatingKey,
            onSetAutomation = onSetAutomation,
            highlight = true,
        )
        AutomationToggle(
            title = "联盟自动捐献",
            detail = "随机挑一个可捐档位捐献给正在研究的联盟科技；进度满就停，不会花金币重置科技",
            settingKey = "allianceDonate",
            enabled = settings?.allianceDonate == true,
            updatingKey = updatingKey,
            onSetAutomation = onSetAutomation,
        )
        AutomationToggle(
            title = "联盟自动签到",
            detail = "每天自动领取联盟签到奖励（连续签到天数会累积）",
            settingKey = "allianceSignIn",
            enabled = settings?.allianceSignIn == true,
            updatingKey = updatingKey,
            onSetAutomation = onSetAutomation,
        )
        AutomationToggle(
            title = "一键完成自动执行",
            detail = "每天自动跑一次游戏里「一键完成」的无损项：资源收取 / 科研工坊 / 文明结晶 / 宝石挖掘(免费次数内)；试炼招募那些烧金币的故意不跑",
            settingKey = "assistAuto",
            enabled = settings?.assistAuto == true,
            updatingKey = updatingKey,
            onSetAutomation = onSetAutomation,
        )
        Spacer(Modifier.height(6.dp))
        Text(
            "规则会保存到当前控制台。后台风险守护开启时，也会按这些规则刷新。",
            color = CokPalette.dim2,
            fontSize = 11.sp,
            lineHeight = 16.sp,
        )
    }
}

@Composable
private fun AutomationTabs(selected: AutomationView, onSelect: (AutomationView) -> Unit) {
    Row(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(7.dp)).background(CokPalette.surfaceHigher),
        horizontalArrangement = Arrangement.SpaceEvenly,
    ) {
        AutomationView.entries.forEach { tab ->
            Text(
                tab.label,
                color = if (tab == selected) CokPalette.accentText else CokPalette.dim2,
                fontSize = 12.sp,
                fontWeight = if (tab == selected) FontWeight.SemiBold else FontWeight.Normal,
                modifier = Modifier.weight(1f).clickable { onSelect(tab) }.padding(vertical = 9.dp),
                textAlign = androidx.compose.ui.text.style.TextAlign.Center,
            )
        }
    }
}

@Composable
private fun AutomationTaskList(
    rules: List<AutomationRule>,
    alerts: List<AutomationAlert>,
    operationInFlight: String?,
    onRecheck: (String) -> Unit,
) {
    if (rules.isEmpty()) {
        Text("正在读取任务状态", color = CokPalette.dim, fontSize = 12.sp)
        return
    }
    Column(verticalArrangement = Arrangement.spacedBy(7.dp)) {
        alerts.forEach { alert ->
            Column(
                Modifier.fillMaxWidth().clip(RoundedCornerShape(7.dp))
                    .background(CokPalette.err.copy(alpha = .12f))
                    .border(1.dp, CokPalette.err.copy(alpha = .42f), RoundedCornerShape(7.dp)).padding(10.dp),
            ) {
                Text("${alert.label}需要处理", color = CokPalette.err, fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
                Text(alert.reason.ifBlank { "自动化执行失败" }, color = CokPalette.dim, fontSize = 11.sp, maxLines = 3)
                Text("连续失败 ${alert.failures} 次${if (alert.inBackoff) " · 正在安全退避" else ""}", color = CokPalette.warn, fontSize = 10.sp)
                OutlinedButton(
                    onClick = { onRecheck(alert.key) },
                    enabled = operationInFlight == null,
                    shape = RoundedCornerShape(6.dp),
                    contentPadding = PaddingValues(horizontal = 10.dp, vertical = 0.dp),
                ) { Text("重新检查", color = CokPalette.accentText, fontSize = 11.sp) }
            }
        }
        rules.forEach { rule ->
            val color = automationStatusColor(rule.status)
            Row(
                Modifier.fillMaxWidth().clip(RoundedCornerShape(7.dp)).background(CokPalette.surfaceHigher).padding(10.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Column(Modifier.weight(1f)) {
                    Text(rule.label, color = CokPalette.fg, fontSize = 13.sp, fontWeight = FontWeight.Medium)
                    Text(rule.reason.ifBlank { "等待下一次检查" }, color = CokPalette.dim2, fontSize = 11.sp, maxLines = 2)
                    if (rule.failures > 0) Text("连续失败 ${rule.failures} 次", color = CokPalette.warn, fontSize = 10.sp)
                }
                Text(automationStatusLabel(rule.status), color = color, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
            }
        }
    }
}

@Composable
private fun AutomationHistoryList(history: List<AutomationHistoryItem>) {
    var source by rememberSaveable { mutableStateOf("all") }
    var expandedId by rememberSaveable { mutableStateOf<String?>(null) }
    val filtered = history.filter { source == "all" || it.source == source }
    Column(verticalArrangement = Arrangement.spacedBy(7.dp)) {
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            listOf("all" to "全部", "auto" to "自动", "manual" to "手动").forEach { (key, label) ->
                Text(label, color = if (source == key) CokPalette.accentText else CokPalette.dim2, fontSize = 11.sp,
                    modifier = Modifier.clickable { source = key }.padding(vertical = 2.dp))
            }
        }
        if (filtered.isEmpty()) Text("还没有可展示的执行记录", color = CokPalette.dim, fontSize = 12.sp)
        filtered.take(16).forEach { entry ->
            val color = automationStatusColor(entry.status)
            Column(
                Modifier.fillMaxWidth().clip(RoundedCornerShape(7.dp)).background(CokPalette.surfaceHigher)
                    .clickable { expandedId = if (expandedId == entry.id) null else entry.id }.padding(10.dp),
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(entry.summary.ifBlank { entry.rule }, color = CokPalette.fg, fontSize = 12.sp, modifier = Modifier.weight(1f), maxLines = 2)
                    Text(automationStatusLabel(entry.status), color = color, fontSize = 10.sp)
                }
                Text(entry.reason.takeIf { it.isNotBlank() } ?: entry.rule, color = CokPalette.dim2, fontSize = 10.sp, maxLines = 2)
                if (expandedId == entry.id) {
                    Spacer(Modifier.height(5.dp))
                    Text(
                        "${if (entry.source == "manual") "人工操作" else "自动执行"} · ${formatAutomationTime(entry.timestamp)} · 规则 ${entry.rule}",
                        color = CokPalette.dim, fontSize = 10.sp, lineHeight = 15.sp,
                    )
                }
            }
        }
    }
}

@Composable
private fun AutomationPolicyPanel(policy: AutomationPolicy?, saving: Boolean, onSave: (Boolean, String, Int, Int, String, Int, Int, Int) -> Unit) {
    var paused by remember(policy?.paused) { mutableStateOf(policy?.paused == true) }
    var mode by remember(policy?.mode) { mutableStateOf(policy?.mode ?: "execute") }
    var failures by remember(policy?.maxFailures) { mutableIntStateOf(policy?.maxFailures ?: 3) }
    var backoff by remember(policy?.backoffMinutes) { mutableIntStateOf(policy?.backoffMinutes ?: 15) }
    var alertLevel by remember(policy?.alertLevel) { mutableStateOf(policy?.alertLevel ?: "failures") }
    var stamina by remember(policy?.huntMinStamina) { mutableIntStateOf(policy?.huntMinStamina ?: 18) }
    var skyPower by remember(policy?.skyMinPower) { mutableIntStateOf(policy?.skyMinPower ?: 0) }
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text("暂停全部自动化", color = if (paused) CokPalette.warn else CokPalette.fg, fontSize = 13.sp, fontWeight = FontWeight.Medium)
                Text("保留规则，但不再写入游戏", color = CokPalette.dim2, fontSize = 11.sp)
            }
            Switch(checked = paused, onCheckedChange = { paused = it }, enabled = !saving)
        }
        Text("运行模式", color = CokPalette.dim2, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
            listOf("execute" to "自动执行", "notify" to "仅提醒").forEach { (key, label) ->
                OutlinedButton(onClick = { mode = key }, modifier = Modifier.weight(1f), shape = RoundedCornerShape(7.dp),
                    colors = ButtonDefaults.outlinedButtonColors(containerColor = if (mode == key) CokPalette.accent.copy(alpha = .14f) else Color.Transparent)) {
                    Text(label, color = if (mode == key) CokPalette.accentText else CokPalette.dim, fontSize = 12.sp)
                }
            }
        }
        NumericStepper("连续失败上限", failures, 1, 12, 1, { failures = it }, suffix = " 次")
        NumericStepper("失败退避", backoff, 1, 120, 1, { backoff = it }, suffix = " 分钟")
        Text("异常提醒", color = CokPalette.dim2, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
        Row(horizontalArrangement = Arrangement.spacedBy(6.dp), modifier = Modifier.fillMaxWidth()) {
            listOf("all" to "每次失败", "failures" to "连续失败", "off" to "关闭").forEach { (key, label) ->
                OutlinedButton(onClick = { alertLevel = key }, modifier = Modifier.weight(1f), shape = RoundedCornerShape(6.dp),
                    contentPadding = PaddingValues(horizontal = 2.dp, vertical = 0.dp),
                    colors = ButtonDefaults.outlinedButtonColors(containerColor = if (alertLevel == key) CokPalette.accent.copy(alpha = .14f) else Color.Transparent)) {
                    Text(label, color = if (alertLevel == key) CokPalette.accentText else CokPalette.dim, fontSize = 10.sp)
                }
            }
        }
        NumericStepper("打怪最低体力", stamina, 0, 500, 1, { stamina = it }, suffix = " 点")
        NumericStepper("天空战力保留", skyPower, 0, 1_000_000, 10_000, { skyPower = it })
        Text("港口资源保留需服务端提供可核验的货物数据，当前不会以猜测数据阻断自动分派。", color = CokPalette.dim2, fontSize = 10.sp, lineHeight = 15.sp)
        PrimaryAction(if (paused) "保存并暂停" else "保存安全策略", saving, Modifier.fillMaxWidth(), saving) {
            onSave(paused, mode, failures, backoff, alertLevel, stamina, skyPower, 0)
        }
    }
}

private fun formatAutomationTime(timestamp: Long): String {
    if (timestamp <= 0) return "时间未知"
    val seconds = (System.currentTimeMillis() / 1000L - timestamp).coerceAtLeast(0L)
    return when {
        seconds < 60 -> "刚刚"
        seconds < 3600 -> "${seconds / 60} 分钟前"
        seconds < 86400 -> "${seconds / 3600} 小时前"
        else -> "${seconds / 86400} 天前"
    }
}

private fun automationStatusLabel(status: String): String = when (status) {
    "success" -> "已完成"
    "failed" -> "失败"
    "skipped" -> "已跳过"
    "paused" -> "已暂停"
    "notify" -> "仅提醒"
    "disabled" -> "未开启"
    else -> "等待中"
}

private fun automationStatusColor(status: String): Color = when (status) {
    "success" -> CokPalette.ok
    "failed" -> CokPalette.err
    "skipped", "paused", "notify" -> CokPalette.warn
    else -> CokPalette.dim2
}

@Composable
private fun ActionOutcomeCard(outcome: ActionOutcome) {
    val color = when {
        !outcome.succeeded -> CokPalette.err
        outcome.snapshotVerified -> CokPalette.ok
        else -> CokPalette.warn
    }
    Column(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(10.dp))
            .background(color.copy(alpha = .12f)).border(1.dp, color.copy(alpha = .42f), RoundedCornerShape(10.dp)).padding(12.dp),
    ) {
        Text(
            when {
                !outcome.succeeded -> "操作未完成 · ${outcome.title}"
                outcome.snapshotVerified -> "操作已确认 · ${outcome.title}"
                else -> "正在确认 · ${outcome.title}"
            },
            color = color,
            fontSize = 13.sp,
            fontWeight = FontWeight.SemiBold,
        )
        Spacer(Modifier.height(3.dp))
        Text(outcome.detail, color = CokPalette.dim, fontSize = 11.sp, lineHeight = 16.sp)
    }
}

@Composable
private fun AutomationRuntimeSummary(
    runtime: AutomationRuntime?,
    settings: AutomationSettings?,
    backgroundMonitoringEnabled: Boolean,
) {
    val enabled = settings?.enabledCount ?: 0
    Column(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(8.dp)).background(CokPalette.surfaceHigher).padding(10.dp),
        verticalArrangement = Arrangement.spacedBy(3.dp),
    ) {
        Text("运行状态", color = CokPalette.dim2, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
        Text(
            "$enabled 项规则已启用 · 最近 ${runtime?.lastPoll ?: "尚未刷新"}",
            color = CokPalette.fg,
            fontSize = 12.sp,
        )
        if (settings?.autoShield == true) {
            val watch = if (runtime?.autoShieldPersistent == true) {
                "推送监听中 · 心跳 ${runtime.shieldWatchTicks} 次${runtime.shieldWatchIntervalSeconds.takeIf { it > 0 }?.let { " · 每 $it 秒" }.orEmpty()}"
            } else "正在等待常驻连接建立"
            Text("自动保护：$watch", color = CokPalette.ok, fontSize = 11.sp)
        }
        Text(
            if (backgroundMonitoringEnabled) "后台风险守护：运行中 · 5 分钟刷新一次" else "后台风险守护：未开启",
            color = if (backgroundMonitoringEnabled) CokPalette.ok else CokPalette.dim2,
            fontSize = 11.sp,
        )
        runtime?.latestAutomaticEvent?.let { event ->
            Text("最近自动处理：${automaticEventSummary(event)} · ${event.time}", color = CokPalette.dim, fontSize = 11.sp, maxLines = 2)
        }
    }
}

private fun automaticEventSummary(event: ConsoleEvent): String = when (event.kind) {
    "dock_auto" -> "港口自动处理"
    "sky_auto" -> "天空之境自动处理"
    "welfare_auto" -> "福利自动领取"
    "score_auto" -> "积分任务自动领取"
    "sign" -> "自动签到"
    "shield_trigger", "shield_result" -> "自动保护已触发"
    else -> event.message.take(48)
}

@Composable
private fun AutomationToggle(
    title: String,
    detail: String,
    settingKey: String,
    enabled: Boolean,
    updatingKey: String?,
    onSetAutomation: (String, Boolean, String) -> Unit,
    highlight: Boolean = false,
) {
    val updating = updatingKey == settingKey
    Row(
        Modifier.fillMaxWidth().padding(vertical = 7.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(Modifier.weight(1f)) {
            Text(title, color = if (highlight) CokPalette.warn else CokPalette.fg, fontSize = 13.sp, fontWeight = FontWeight.Medium)
            Spacer(Modifier.height(2.dp))
            Text(detail, color = CokPalette.dim2, fontSize = 11.sp, lineHeight = 15.sp)
        }
        if (updating) {
            CircularProgressIndicator(Modifier.size(22.dp), color = CokPalette.accent, strokeWidth = 2.dp)
        } else {
            Switch(
                checked = enabled,
                enabled = updatingKey == null,
                onCheckedChange = { onSetAutomation(settingKey, it, title) },
            )
        }
    }
}

@Composable
private fun AdvancedConsoleCard(onOpenConsole: () -> Unit) {
    Column(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(10.dp))
            .background(CokPalette.surface)
            .border(1.dp, CokPalette.line, RoundedCornerShape(10.dp))
            .padding(14.dp),
    ) {
        Text("完整高级控制台", color = CokPalette.fg, fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
        Spacer(Modifier.height(4.dp))
        Text("用于低频配置：编队编辑、地图扫描、定位、渠道登录与完整明细。", color = CokPalette.dim, fontSize = 12.sp, lineHeight = 17.sp)
        Spacer(Modifier.height(12.dp))
        OutlinedButton(onClick = onOpenConsole, modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(8.dp)) {
            Text("打开高级控制台", color = CokPalette.accentText)
        }
    }
}

@Composable
private fun DailyActions(inFlight: QuickAction?, operationBusy: Boolean, onAction: (QuickAction) -> Unit) {
    val disabled = inFlight != null || operationBusy
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        PrimaryAction("一键收取领地资源", disabled, Modifier.fillMaxWidth(), inFlight == QuickAction.ASSIST) {
            onAction(QuickAction.ASSIST)
        }
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
            SecondaryAction("签到", disabled, Modifier.weight(1f), inFlight == QuickAction.SIGN) { onAction(QuickAction.SIGN) }
            SecondaryAction("福利", disabled, Modifier.weight(1f), inFlight == QuickAction.WELFARE_CLAIM) { onAction(QuickAction.WELFARE_CLAIM) }
            SecondaryAction("港口", disabled, Modifier.weight(1f), inFlight == QuickAction.DOCK_REWARD) { onAction(QuickAction.DOCK_REWARD) }
        }
    }
}

@Composable
private fun SafetyCard(
    operations: OperationsSnapshot?,
    busy: String?,
    onUseShield: (ShieldSlot, ShieldItem) -> Unit,
) {
    val protected = operations?.shieldActive == true
    var showManualShield by rememberSaveable(protected) { mutableStateOf(!protected) }
    Column(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(10.dp))
            .background(if (protected) CokPalette.surface else CokPalette.err.copy(alpha = .12f))
            .border(1.dp, if (protected) CokPalette.line else CokPalette.err.copy(alpha = .65f), RoundedCornerShape(10.dp))
            .padding(14.dp),
    ) {
        Text(if (protected) "保护罩已生效" else "当前没有保护罩", color = if (protected) CokPalette.fg else CokPalette.err, fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
        Spacer(Modifier.height(4.dp))
        Text(operations?.shieldStatus ?: "正在读取保护状态", color = CokPalette.dim, fontSize = 12.sp)
        Spacer(Modifier.height(12.dp))
        Text(
            if (operations?.automation?.autoShield == true) "自动保护已开启 · 会保持游戏连接以接收攻击提醒"
            else "自动保护未开启 · 可在上方“自动处理”中配置",
            color = CokPalette.dim2,
            fontSize = 11.sp,
            lineHeight = 16.sp,
        )
        val configuredSlots = operations?.shieldSlots.orEmpty().filter { it.items.isNotEmpty() }
        if (configuredSlots.isNotEmpty()) {
            Spacer(Modifier.height(12.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.weight(1f)) {
                    Text("手动开启", color = CokPalette.dim2, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
                    Text(
                        if (protected) "当前保护罩仍有效" else "使用已配置槽位中的保护罩道具",
                        color = CokPalette.dim,
                        fontSize = 11.sp,
                    )
                }
                IconButton(onClick = { showManualShield = !showManualShield }) {
                    Icon(
                        if (showManualShield) Icons.Filled.KeyboardArrowUp else Icons.Filled.KeyboardArrowDown,
                        contentDescription = if (showManualShield) "收起手动开罩" else "展开手动开罩",
                        tint = CokPalette.accentText,
                    )
                }
            }
            if (showManualShield) {
                configuredSlots.forEach { slot ->
                    slot.items.forEach { item ->
                        Spacer(Modifier.height(7.dp))
                        OutlinedButton(
                            onClick = { onUseShield(slot, item) },
                            enabled = busy == null,
                            modifier = Modifier.fillMaxWidth(),
                            shape = RoundedCornerShape(8.dp),
                        ) {
                            Text(
                                "${slot.name} · ${item.name}${item.count.takeIf { it > 0 }?.let { " · 库存 $it" } ?: ""}",
                                color = CokPalette.accentText,
                                fontSize = 12.sp,
                                maxLines = 1,
                            )
                        }
                    }
                }
            }
        } else if (!protected) {
            Spacer(Modifier.height(10.dp))
            Text("未读取到可用的保护罩槽位，请在高级控制台配置后再开启。", color = CokPalette.warn, fontSize = 11.sp, lineHeight = 16.sp)
        }
        if (operations?.runningQueues?.isNotEmpty() == true) {
            Spacer(Modifier.height(12.dp))
            Text("进行中的队列", color = CokPalette.dim2, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
            operations.runningQueues.take(2).forEach { queue ->
                Spacer(Modifier.height(5.dp))
                Text("${queue.name} · ${queue.detail}", color = CokPalette.dim, fontSize = 12.sp)
            }
        }
    }
}

@Composable
private fun QueueSpeedupCard(
    queues: List<QueueStatus>,
    items: List<SpeedupItem>,
    busy: String?,
    onUseItem: (QueueStatus, SpeedupItem, Int) -> Unit,
    onUseGold: (QueueStatus) -> Unit,
) {
    var selectedQueue by remember(queues) { mutableStateOf(queues.firstOrNull()) }
    var selectedItem by remember(items) { mutableStateOf(items.firstOrNull()) }
    var itemCount by remember(selectedItem?.uuid) { mutableIntStateOf(1) }
    val queue = selectedQueue?.takeIf { it in queues } ?: queues.firstOrNull()
    val item = selectedItem?.takeIf { it in items } ?: items.firstOrNull()
    val safeItemCount = item?.let { itemCount.coerceIn(1, it.count) } ?: 1

    Column(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(10.dp)).background(CokPalette.surface)
            .border(1.dp, CokPalette.line, RoundedCornerShape(10.dp)).padding(14.dp),
    ) {
        Text("进行中队列", color = CokPalette.fg, fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
        Spacer(Modifier.height(4.dp))
        if (queues.isEmpty()) {
            Text("当前没有可加速的建造或训练队列", color = CokPalette.dim, fontSize = 12.sp)
            return@Column
        }
        Text("选择一个队列后再决定是否加速", color = CokPalette.dim, fontSize = 12.sp)
        Spacer(Modifier.height(10.dp))
        queues.forEach { candidate ->
            QueueChoice(candidate, candidate.uuid == queue?.uuid) { selectedQueue = candidate }
            Spacer(Modifier.height(6.dp))
        }
        Spacer(Modifier.height(6.dp))
        Text("使用道具", color = CokPalette.dim2, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
        if (item == null) {
            Spacer(Modifier.height(4.dp))
            Text("未读到可用加速道具，仍可选择金币加速", color = CokPalette.dim, fontSize = 12.sp)
        } else {
            Spacer(Modifier.height(7.dp))
            items.forEach { candidate ->
                ItemChoice(candidate, candidate.uuid == item.uuid) {
                    selectedItem = candidate
                    itemCount = 1
                }
                Spacer(Modifier.height(6.dp))
            }
            Spacer(Modifier.height(8.dp))
            NumericStepper("使用数量", safeItemCount, 1, item.count, 1, { itemCount = it }, suffix = " 个")
            Spacer(Modifier.height(8.dp))
            PrimaryAction("确认使用道具", busy != null, Modifier.fillMaxWidth(), busy == "speedup-item") {
                onUseItem(queue ?: return@PrimaryAction, item, safeItemCount)
            }
        }
        Spacer(Modifier.height(10.dp))
        OutlinedButton(
            onClick = { queue?.let(onUseGold) }, enabled = busy == null,
            modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(8.dp),
            colors = ButtonDefaults.outlinedButtonColors(contentColor = CokPalette.err),
        ) { LoadingLabel("金币加速", busy == "speedup-gold", CokPalette.err) }
    }
}

@Composable
private fun DockCard(dock: DockStatus?, busy: String?, onClaim: () -> Unit) {
    val status = dock ?: return
    Column(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(10.dp)).background(CokPalette.surface)
            .border(1.dp, CokPalette.line, RoundedCornerShape(10.dp)).padding(14.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text("港口贸易", color = CokPalette.fg, fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
                Text(
                    when {
                        status.disabled -> "当前账号暂未开放港口功能"
                        !status.available -> "正在读取港口贸易状态"
                        else -> "可领 ${status.rewardable} · 在途 ${status.trading} · 空闲 ${status.idle}${status.shipLimit.takeIf { it > 0 }?.let { " / $it 船位" }.orEmpty()}"
                    },
                    color = if (status.disabled) CokPalette.dim2 else CokPalette.dim,
                    fontSize = 12.sp,
                )
            }
            Text(
                if (status.rewardable > 0 || status.cargoClaimable) "可领取" else "正常",
                color = if (status.rewardable > 0 || status.cargoClaimable) CokPalette.warn else CokPalette.ok,
                fontSize = 12.sp,
                fontWeight = FontWeight.SemiBold,
            )
        }
        status.note.takeIf { it.isNotBlank() }?.let {
            Spacer(Modifier.height(7.dp)); Text(it, color = CokPalette.dim2, fontSize = 11.sp, lineHeight = 16.sp)
        }
        status.lastReward.takeIf { it.isNotBlank() }?.let {
            Spacer(Modifier.height(5.dp)); Text(it, color = CokPalette.dim2, fontSize = 11.sp)
        }
        status.lastAutomaticRun.takeIf { it.isNotBlank() }?.let {
            Spacer(Modifier.height(5.dp)); Text("最近自动处理 · $it", color = CokPalette.dim2, fontSize = 11.sp, maxLines = 2)
        }
        if (!status.disabled && status.available) {
            Spacer(Modifier.height(12.dp))
            PrimaryAction(
                if (status.rewardable > 0 || status.cargoClaimable) "领取港口奖励" else "检查并领取港口奖励",
                busy != null,
                Modifier.fillMaxWidth(),
                busy == QuickAction.DOCK_REWARD.name,
                onClick = onClaim,
            )
        }
    }
}

@Composable
private fun QueueChoice(queue: QueueStatus, selected: Boolean, onClick: () -> Unit) {
    OutlinedButton(
        onClick = onClick, modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(7.dp),
        colors = ButtonDefaults.outlinedButtonColors(
            containerColor = if (selected) CokPalette.accent.copy(alpha = .12f) else Color.Transparent,
            contentColor = CokPalette.fg,
        ),
    ) {
        Column(Modifier.fillMaxWidth()) {
            Text("${queue.name} · ${queue.detail}", fontSize = 12.sp, maxLines = 1)
            Text("剩余 ${formatQueueDuration(queue.remainingMillis)}", color = CokPalette.dim, fontSize = 10.sp)
        }
    }
}

@Composable
private fun ItemChoice(item: SpeedupItem, selected: Boolean, onClick: () -> Unit) {
    OutlinedButton(
        onClick = onClick, modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(7.dp),
        colors = ButtonDefaults.outlinedButtonColors(
            containerColor = if (selected) CokPalette.accent.copy(alpha = .12f) else Color.Transparent,
            contentColor = CokPalette.fg,
        ),
    ) {
        Column(Modifier.fillMaxWidth()) {
            Text("${item.name} · 库存 ${item.count}", fontSize = 12.sp, maxLines = 1)
            Text(item.label.ifBlank { item.seconds.takeIf { it > 0 }?.let { "每个约 ${formatQueueDuration(it * 1000)}" } ?: "加速道具" }, color = CokPalette.dim, fontSize = 10.sp, maxLines = 1)
        }
    }
}

@Composable
private fun HuntCard(
    hunt: HuntStatus?,
    dataAvailable: Boolean,
    unavailableReason: String,
    level: Int,
    squads: Int,
    soldiersPerSquad: Int,
    maxKills: Int,
    mix: Int,
    autoStamina: Boolean,
    busy: String?,
    onLevelChange: (Int) -> Unit,
    onSquadsChange: (Int) -> Unit,
    onSoldiersChange: (Int) -> Unit,
    onMaxKillsChange: (Int) -> Unit,
    onMixChange: (Int) -> Unit,
    onAutoStaminaChange: (Boolean) -> Unit,
    saving: Boolean,
    onSavePlan: () -> Unit,
    onStart: () -> Unit,
    onStop: () -> Unit,
) {
    val running = hunt?.isRunning == true
    var showSetup by rememberSaveable { mutableStateOf(false) }
    Column(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(10.dp)).background(CokPalette.surface)
            .border(1.dp, CokPalette.line, RoundedCornerShape(10.dp)).padding(14.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text("自动打怪", color = CokPalette.fg, fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
                Text(
                    if (running) "运行中 · 已完成 ${hunt?.kills ?: 0} 只" else "按空闲兵种自动分配队伍",
                    color = if (running) CokPalette.ok else CokPalette.dim,
                    fontSize = 12.sp,
                )
            }
            Text(
                if (dataAvailable) "${hunt?.stamina} / ${hunt?.staminaMax}" else "未同步",
                color = if (dataAvailable) CokPalette.accentText else CokPalette.dim2,
                fontSize = if (dataAvailable) 18.sp else 13.sp,
                fontWeight = FontWeight.Bold,
            )
            if (!running) {
                IconButton(onClick = { showSetup = !showSetup }) {
                    Icon(
                        if (showSetup) Icons.Filled.KeyboardArrowUp else Icons.Filled.KeyboardArrowDown,
                        contentDescription = if (showSetup) "收起打怪计划" else "配置打怪计划",
                        tint = CokPalette.accentText,
                    )
                }
            }
        }
        Spacer(Modifier.height(12.dp))
        if (running) {
            HuntProgress(hunt)
        } else if (showSetup) {
            NumericStepper("目标等级", level, 1, 30, 1, onLevelChange)
            Spacer(Modifier.height(8.dp))
            NumericStepper("并行队数", squads, 1, 8, 1, onSquadsChange, suffix = " 队")
            Spacer(Modifier.height(8.dp))
            // 上限不是 2w: 标准兵种库存天花板就是 1.8~2 万, 活动兵种能到几十万,
            // 实际派出量 = min(这里填的, 该兵种空闲兵)。所以要给足空间并支持键入。
            NumericField("每队兵力", soldiersPerSquad, 1, 999_999, 500, onSoldiersChange, suffix = " 人")
            Spacer(Modifier.height(8.dp))
            NumericStepper(
                "每队兵种",
                mix,
                1,
                4,
                1,
                onMixChange,
                valueText = "$mix 种",
            )
            Spacer(Modifier.height(8.dp))
            NumericStepper(
                "最大击杀",
                maxKills,
                0,
                500,
                1,
                onMaxKillsChange,
                valueText = if (maxKills == 0) "不限" else "$maxKills 只",
            )
            Spacer(Modifier.height(10.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.weight(1f)) {
                    Text("体力不足自动喝体力药水", color = CokPalette.fg, fontSize = 13.sp, fontWeight = FontWeight.Medium)
                    Text("体力不够时自动用背包里的体力药水（10/50/100 体力），会消耗药水", color = CokPalette.dim2, fontSize = 11.sp)
                }
                Switch(checked = autoStamina, onCheckedChange = { onAutoStaminaChange(it) })
            }
            Spacer(Modifier.height(10.dp))
            Text(
                "单轮最多派 $squads 队，理论消耗约 ${squads * HUNT_STAMINA_COST} 点体力；实际以游戏结算为准。",
                color = CokPalette.dim2,
                fontSize = 11.sp,
                lineHeight = 16.sp,
            )
            Text(
                if (mix <= 1) {
                    "每队用一种兵；同一种兵可以拆成多队，所以队数按库存来。"
                } else {
                    "每队最多 $mix 种兵（混编）：一次出征带多种兵，只有同类兵能混编（普通兵之间 / 活动兵之间），跨类会被拒绝。"
                },
                color = CokPalette.dim2,
                fontSize = 11.sp,
                lineHeight = 16.sp,
            )
            Text(
                "你填的每队兵力是上限：库存不够摊满 $squads 队时，会按库存自动摊薄每队人数，保证 $squads 队都能开出来。",
                color = CokPalette.dim2,
                fontSize = 11.sp,
                lineHeight = 16.sp,
            )
            Spacer(Modifier.height(10.dp))
            OutlinedButton(
                onClick = onSavePlan,
                enabled = !saving && busy == null,
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(8.dp),
            ) { LoadingLabel("保存为默认打怪方案", saving, CokPalette.accentText) }
        } else {
            Text(
                if (dataAvailable) {
                    "默认计划：等级 $level · $squads 队 · 每队 $soldiersPerSquad 人 · 每队 ${if (mix <= 1) "1 种兵" else "$mix 种兵"}${if (maxKills == 0) " · 不限击杀" else " · 最多 $maxKills 只"}" +
                        (if (autoStamina) " · 体力不足自动喝药水" else "")
                } else {
                    "体力与打怪配置暂未同步${unavailableReason.takeIf { it.isNotBlank() }?.let { "：$it" } ?: "，请刷新后再试"}"
                },
                color = CokPalette.dim,
                fontSize = 12.sp,
                lineHeight = 17.sp,
            )
        }
        Spacer(Modifier.height(12.dp))
        if (running) {
            OutlinedButton(onClick = onStop, enabled = busy == null, modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(8.dp)) {
                LoadingLabel("停止打怪", busy == "hunt-stop", CokPalette.err)
            }
        } else {
            PrimaryAction("开始打怪", busy != null || !dataAvailable, Modifier.fillMaxWidth(), onClick = onStart)
        }
    }
}

@Composable
private fun SkyCard(
    sky: SkyStatus?,
    busy: String?,
    onClaim: () -> Unit,
    onExplore: () -> Unit,
) {
    Column(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(10.dp)).background(CokPalette.surface)
            .border(1.dp, CokPalette.line, RoundedCornerShape(10.dp)).padding(14.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text("天空之境", color = CokPalette.fg, fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
                Text(sky?.stateText ?: "正在读取探索状态", color = CokPalette.dim, fontSize = 12.sp)
            }
        }
        if (sky?.reason?.isNotBlank() == true) {
            Spacer(Modifier.height(6.dp)); Text(sky.reason, color = CokPalette.dim2, fontSize = 11.sp)
        }
        val skyDetail = buildList {
            sky?.level?.takeIf { it > 0 }?.let { add("探索等级 $it") }
            sky?.remaining?.takeIf { it > 0 }?.let { add("剩余 ${formatQueueDuration(it * 1_000)}") }
            if ((sky?.requiredPower ?: 0) > 0) add("战力 ${sky?.currentPower ?: 0} / ${sky?.requiredPower}")
        }.joinToString(" · ")
        if (skyDetail.isNotBlank()) {
            Spacer(Modifier.height(7.dp))
            Text(skyDetail, color = CokPalette.dim2, fontSize = 11.sp)
        }
        sky?.lastAutomaticRun?.takeIf { it.isNotBlank() }?.let {
            Spacer(Modifier.height(4.dp)); Text("上次自动处理 · $it", color = CokPalette.dim2, fontSize = 11.sp)
        }
        Spacer(Modifier.height(12.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
            SecondaryAction(
                label = "领取奖励",
                disabled = busy != null || sky?.canClaim != true,
                modifier = Modifier.weight(1f),
                loading = busy == "sky-reward",
                onClick = onClaim,
            )
            PrimaryAction("开始探索", busy != null || sky?.canExplore != true, Modifier.weight(1f), onClick = onExplore)
        }
    }
}

@Composable
private fun HuntProgress(hunt: HuntStatus?) {
    val status = hunt ?: return
    val target = status.maxKills.takeIf { it > 0 }
    val headline = if (target != null) "${status.kills} / $target 只" else "已完成 ${status.kills} 只"
    Text(headline, color = CokPalette.accentText, fontSize = 18.sp, fontWeight = FontWeight.Bold)
    val progress = target?.let { status.kills.toFloat() / it.toFloat() }
    if (progress != null) {
        Spacer(Modifier.height(5.dp))
        androidx.compose.material3.LinearProgressIndicator(
            progress = { progress.coerceIn(0f, 1f) },
            modifier = Modifier.fillMaxWidth(),
            color = CokPalette.accent,
            trackColor = CokPalette.surfaceHigher,
        )
    }
    (status.waitFor.ifBlank { status.note }).takeIf { it.isNotBlank() }?.let {
        Spacer(Modifier.height(7.dp))
        Text(it, color = CokPalette.dim, fontSize = 12.sp)
    }
    if (status.failures > 0) {
        Spacer(Modifier.height(4.dp))
        Text("异常重试 ${status.failures} 次", color = CokPalette.warn, fontSize = 11.sp)
    }
    if (status.staminaPotions > 0) {
        Spacer(Modifier.height(4.dp))
        Text("已喝体力药水 ${status.staminaPotions} 瓶", color = CokPalette.accentText, fontSize = 11.sp)
    }
    if (status.squads.isNotEmpty()) {
        Spacer(Modifier.height(12.dp))
        Text("队伍进度", color = CokPalette.dim2, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
        status.squads.forEach { squad ->
            Spacer(Modifier.height(7.dp))
            HuntSquadRow(squad)
        }
    }
}

@Composable
private fun HuntSquadRow(squad: HuntSquadStatus) {
    val stateText = when (squad.state) {
        "marching" -> "出征中"
        "done" -> "已返回"
        else -> squad.note.ifBlank { "待命" }
    }
    Row(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(7.dp)).background(CokPalette.surfaceHigher).padding(horizontal = 10.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text("${squad.slot}", color = CokPalette.dim2, fontSize = 12.sp, modifier = Modifier.width(22.dp))
        Column(Modifier.weight(1f)) {
            // 混编队: 名字是 "A + B", 数量按兵种拆开显示
            val troopText = if (squad.troops.size > 1) {
                squad.troops.joinToString(" + ") { "${it.name} ${it.num}" } + " 人"
            } else {
                "${squad.soldiers} 人"
            }
            Text("${squad.name} · $troopText", color = CokPalette.fg, fontSize = 12.sp, maxLines = 1)
            val detail = listOfNotNull(
                squad.target.takeIf { it.isNotBlank() },
                squad.elapsedSeconds.takeIf { it > 0 }?.let { "${it}s" },
            ).joinToString(" · ")
            if (detail.isNotBlank()) Text(detail, color = CokPalette.dim2, fontSize = 10.sp)
        }
        Text("$stateText · ${squad.kills}", color = if (squad.state == "marching") CokPalette.ok else CokPalette.dim, fontSize = 11.sp)
    }
}

/**
 * Giant-griffin rally picker.
 *
 * A rally spends stamina and soldiers for real and creates a team in the
 * alliance, so the card only ever *prepares* one; the actual dispatch goes
 * through the confirmation dialog.
 */
@Composable
private fun RallyCard(
    rally: RallyStatus?,
    loading: Boolean,
    busy: String?,
    level: Int,
    onLevelChange: (Int) -> Unit,
    target: Int,
    onTargetChange: (Int) -> Unit,
    slot: Int,
    onSlotChange: (Int) -> Unit,
    soldiers: Int,
    onSoldiersChange: (Int) -> Unit,
    onRefresh: () -> Unit,
    onStart: () -> Unit,
) {
    val bosses = remember(rally, level) {
        val all = rally?.bosses.orEmpty()
        if (level == 0) all else all.filter { it.level == level }
    }
    val levels = rally?.levels.orEmpty()
    val selected = bosses.firstOrNull { it.index == target }
    val mine = rally?.myRallies.orEmpty()
    Column(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(10.dp)).background(CokPalette.surface)
            .border(1.dp, CokPalette.line, RoundedCornerShape(10.dp)).padding(14.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text("巨型狮鹫 · 集结", color = CokPalette.fg, fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
                Text(
                    if (rally?.loaded == true) {
                        "已知 ${rally.known} 只 · 联盟现有集结 ${rally.rallyCount} 支"
                    } else {
                        "活动怪首领 · 联盟集结出征"
                    },
                    color = CokPalette.dim,
                    fontSize = 12.sp,
                )
            }
            if (rally?.stamina != null) {
                Text(
                    "体力 ${rally.stamina}",
                    color = CokPalette.accentText,
                    fontSize = 13.sp,
                    fontWeight = FontWeight.Bold,
                )
            }
            Spacer(Modifier.width(6.dp))
            SecondaryAction("刷新", busy != null, Modifier.width(72.dp), loading = loading) { onRefresh() }
        }

        if (mine.isNotEmpty()) {
            Spacer(Modifier.height(10.dp))
            val first = mine.first()
            Text(
                "集结中 · 目标 ${first.monsterId} · 等待 ${first.waitMinutes.toInt()} 分钟" +
                    if (first.members > 0) " · ${first.members} 人" else "",
                color = CokPalette.ok,
                fontSize = 12.sp,
            )
            Text("同一目标只能有一支集结，打完才能再发", color = CokPalette.dim2, fontSize = 11.sp)
            return@Column
        }

        if (bosses.isEmpty()) {
            Spacer(Modifier.height(12.dp))
            Text(
                if (rally?.loaded == true) "还没扫到该等级的巨型狮鹫，点「刷新」继续扫描" else "点「刷新」读取地图上的巨型狮鹫",
                color = CokPalette.dim2,
                fontSize = 12.sp,
            )
            return@Column
        }

        Spacer(Modifier.height(12.dp))
        Text("等级", color = CokPalette.dim2, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
        Spacer(Modifier.height(6.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            RallyChip("全部", level == 0, Modifier.weight(1f)) { onLevelChange(0) }
            levels.forEach { lv ->
                RallyChip("$lv", level == lv, Modifier.weight(1f)) { onLevelChange(lv) }
            }
        }

        Spacer(Modifier.height(12.dp))
        Text("目标", color = CokPalette.dim2, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
        Spacer(Modifier.height(6.dp))
        bosses.take(4).forEach { boss ->
            Spacer(Modifier.height(4.dp))
            RallyTargetRow(boss, boss.index == target) { onTargetChange(boss.index) }
        }
        if (bosses.size > 4) {
            Spacer(Modifier.height(4.dp))
            Text("还有 ${bosses.size - 4} 只，可换等级缩小范围", color = CokPalette.dim2, fontSize = 11.sp)
        }

        Spacer(Modifier.height(12.dp))
        Text("集结时间(分钟)", color = CokPalette.dim2, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
        Spacer(Modifier.height(6.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            (rally?.slots.orEmpty()).forEach { option ->
                RallyChip("${option.minutes}", slot == option.slot, Modifier.weight(1f)) { onSlotChange(option.slot) }
            }
        }

        Spacer(Modifier.height(12.dp))
        NumericField("派兵", soldiers, 1, 999_999, 100, onSoldiersChange, suffix = " 人")
        Spacer(Modifier.height(4.dp))
        Text(
            "点数字框可直接键入（如 3500），范围 1 ~ 999999；集结派兵只能用标准兵种，实际按库存来",
            color = CokPalette.dim2,
            fontSize = 11.sp,
        )

        Spacer(Modifier.height(12.dp))
        PrimaryAction(
            if (selected == null) "发起集结" else "发起集结（${selected.level} 级）",
            busy != null || selected == null,
            Modifier.fillMaxWidth(),
        ) { onStart() }
        Spacer(Modifier.height(8.dp))
        Text(
            "集结 = 联盟成员一起打，时间越长盟友越容易加入。" +
                "每次消耗约 ${rally?.staminaCost ?: 20} 点体力与所派士兵。",
            color = CokPalette.dim2,
            fontSize = 11.sp,
            lineHeight = 16.sp,
        )
    }
}

@Composable
private fun RallyChip(label: String, selected: Boolean, modifier: Modifier = Modifier, onClick: () -> Unit) {
    OutlinedButton(
        onClick = onClick,
        modifier = modifier,
        shape = RoundedCornerShape(7.dp),
        // 默认内边距会把「60 分钟」这种标签挤掉 —— 4 个档位要在一行里放下
        contentPadding = PaddingValues(horizontal = 2.dp),
        colors = ButtonDefaults.outlinedButtonColors(
            containerColor = if (selected) CokPalette.accent.copy(alpha = .12f) else Color.Transparent,
            contentColor = if (selected) CokPalette.accentText else CokPalette.dim,
        ),
    ) { Text(label, fontSize = 12.sp, maxLines = 1) }
}

@Composable
private fun RallyTargetRow(boss: RallyTarget, selected: Boolean, onClick: () -> Unit) {
    OutlinedButton(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(7.dp),
        colors = ButtonDefaults.outlinedButtonColors(
            containerColor = if (selected) CokPalette.accent.copy(alpha = .12f) else Color.Transparent,
            contentColor = CokPalette.fg,
        ),
    ) {
        Column(Modifier.fillMaxWidth()) {
            Text(
                "${boss.level} 级巨型狮鹫" + if (boss.busy) " · 已有集结" else "",
                fontSize = 12.sp, maxLines = 1,
                color = if (boss.busy) CokPalette.dim else CokPalette.fg,
            )
            val hp = if (boss.maxHp > 0) "${boss.hp} / ${boss.maxHp}" else "血量未知"
            Text("血量 $hp · #${boss.index}", color = CokPalette.dim2, fontSize = 10.sp, maxLines = 1)
        }
    }
}

@Composable
private fun NumericStepper(
    label: String,
    value: Int,
    min: Int,
    max: Int,
    step: Int,
    onChange: (Int) -> Unit,
    suffix: String = "",
    valueText: String = "$value$suffix",
) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Text(label, color = CokPalette.dim, fontSize = 13.sp, modifier = Modifier.weight(1f))
        IconButton(onClick = { onChange((value - step).coerceAtLeast(min)) }, enabled = value > min, modifier = Modifier.size(40.dp)) {
            Text("−", color = CokPalette.accentText, fontSize = 22.sp, fontWeight = FontWeight.Medium)
        }
        Text(valueText, color = CokPalette.fg, fontSize = 14.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.width(76.dp), textAlign = androidx.compose.ui.text.style.TextAlign.Center, maxLines = 1)
        IconButton(onClick = { onChange((value + step).coerceAtMost(max)) }, enabled = value < max, modifier = Modifier.size(40.dp)) {
            Icon(Icons.Filled.Add, contentDescription = "增加$label", tint = CokPalette.accentText)
        }
    }
}

/**
 * 可直接键入的数字输入框（± 按钮同时保留，方便微调）。
 *
 * NumericStepper 只能一点点加减，但「派兵」这种数值经常要精确到个位
 * （例如 3500、12345），必须能直接敲。
 *
 * 实现要点（都是真机踩出来的）：
 *  - **每次点这个框都从零开始敲**：输入框里只装"用户正在敲的内容"，
 *    当前值用灰色占位提示显示。
 *    原因：Compose 1.11 的 BasicTextField 内部状态才是真正的主，
 *    聚焦时会把旧值原样吐回来，而点击落在数字中间会把光标插进去、选区被折叠，
 *    于是敲 "3500" 会变成 "20350000" 这种拼接串。
 *    值不进输入框 → 光标只有 0 一个落点 → 敲什么就是什么。
 *    点按用 pointerInput(Initial) 侦测：按下时打标记，等平台把旧值吐回来时丢弃它。
 *  - 每次输入都把**夹取到 [min]~[max] 之后**的值回写父级，保证父级永远是合法值
 *    （真正发出去的数字以父级为准，确认弹窗里显示的也是它）。
 *  - ± 按钮以"用户实际看到的数"为基准（文本里可能有还没夹取的原始输入）。
 */
@Composable
private fun NumericField(
    label: String,
    value: Int,
    min: Int,
    max: Int,
    step: Int,
    onChange: (Int) -> Unit,
    suffix: String = "",
) {
    var text by remember { mutableStateOf("") }
    var focused by remember { mutableStateOf(false) }
    // 用户刚按了这个框 -> 平台下一帧会把旧值吐回来, 那一次要丢掉
    var pendingClear by remember { mutableStateOf(false) }

    // ± 按钮以"用户实际看到的数"为基准（文本里可能有还没夹取的原始输入）
    fun currentNumber(): Int = text.toIntOrNull() ?: value

    Row(verticalAlignment = Alignment.CenterVertically) {
        Text(label, color = CokPalette.dim, fontSize = 13.sp, modifier = Modifier.weight(1f))
        IconButton(
            onClick = {
                val next = (currentNumber() - step).coerceIn(min, max)
                if (focused) text = "$next"
                onChange(next)
            },
            enabled = currentNumber() > min,
            modifier = Modifier.size(40.dp),
        ) {
            Text("−", color = CokPalette.accentText, fontSize = 22.sp, fontWeight = FontWeight.Medium)
        }
        BasicTextField(
            value = TextFieldValue(text, TextRange(text.length)),
            onValueChange = { next ->
                val raw = next.text.filter { it.isDigit() }.take(9)
                if (pendingClear) {
                    // 刚按过这个框: 只取"新敲进去的那几个字符", 旧值整个丢掉
                    pendingClear = false
                    text = insertedDigits(text, raw)
                } else {
                    text = raw
                }
                val parsed = text.toIntOrNull()
                if (parsed != null) onChange(parsed.coerceIn(min, max))
            },
            singleLine = true,
            textStyle = TextStyle(
                color = CokPalette.fg,
                fontSize = 14.sp,
                fontWeight = FontWeight.SemiBold,
                textAlign = TextAlign.Center,
            ),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            cursorBrush = SolidColor(CokPalette.accentText),
            modifier = Modifier
                .width(96.dp)
                .pointerInput(Unit) {
                    // Initial 通道: 在文本框自己处理之前拿到按下事件, 不消费它
                    awaitPointerEventScope {
                        while (true) {
                            val event = awaitPointerEvent(PointerEventPass.Initial)
                            if (event.changes.any { it.changedToDown() }) {
                                pendingClear = true
                            }
                        }
                    }
                }
                .onFocusChanged { state ->
                    val now = state.isFocused
                    // 聚焦/失焦都清空输入框：每次点开都从零开始敲
                    text = ""
                    focused = now
                },
            decorationBox = { inner ->
                Box(
                    Modifier
                        .fillMaxWidth()
                        .height(38.dp)
                        .clip(RoundedCornerShape(7.dp))
                        .background(CokPalette.surfaceHigh)
                        .border(1.dp, CokPalette.line, RoundedCornerShape(7.dp)),
                    contentAlignment = Alignment.Center,
                ) {
                    // 当前值以灰色占位提示显示（输入框本身是空的）
                    if (text.isEmpty()) {
                        Text(
                            "$value",
                            color = CokPalette.dim2,
                            fontSize = 14.sp,
                            fontWeight = FontWeight.SemiBold,
                            maxLines = 1,
                        )
                    }
                    Box(Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) { inner() }
                }
            },
        )
        if (suffix.isNotEmpty()) {
            Text(suffix, color = CokPalette.dim2, fontSize = 12.sp)
        }
        IconButton(
            onClick = {
                val next = (currentNumber() + step).coerceIn(min, max)
                if (focused) text = "$next"
                onChange(next)
            },
            enabled = currentNumber() < max,
            modifier = Modifier.size(40.dp),
        ) {
            Icon(Icons.Filled.Add, contentDescription = "增加$label", tint = CokPalette.accentText)
        }
    }
}

/**
 * 求两段文本之间"新插入"的字符。
 *
 * 平台把旧值吐回来时, 新的按键可能插在旧值中间(点哪儿光标就在哪儿),
 * 只看整串文本没法区分"敲的"和"旧的", 用公共前后缀做差分就能把新敲的那几个字摘出来。
 */
private fun insertedDigits(old: String, new: String): String {
    if (old == new) return ""
    if (old.isEmpty()) return new
    var prefix = 0
    while (prefix < old.length && prefix < new.length && old[prefix] == new[prefix]) prefix++
    var suffix = 0
    while (
        suffix < old.length - prefix &&
        suffix < new.length - prefix &&
        old[old.length - 1 - suffix] == new[new.length - 1 - suffix]
    ) suffix++
    val end = (new.length - suffix).coerceAtLeast(prefix)
    return new.substring(prefix, end)
}

@Composable
private fun QuickAssistCard(
    assist: QuickAssistStatus?,
    busy: String?,
    costly: Boolean,
    onCostlyChange: (Boolean) -> Unit,
    onRun: () -> Unit,
) {
    Column(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(10.dp)).background(CokPalette.surface)
            .border(1.dp, CokPalette.line, RoundedCornerShape(10.dp)).padding(14.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text("一键完成", color = CokPalette.fg, fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
                Text(
                    assist?.let {
                        if (it.autoEnabled) {
                            "每天自动执行一次" + (if (it.lastDay.isNotBlank()) " · 上次 ${it.lastDay}" else "（今日待执行）")
                        } else {
                            "游戏里那个面板共 ${it.items.size} 项 · 无损 ${it.items.count { i -> i.autoKind == "free" }} 项"
                        }
                    } ?: "正在读取面板清单",
                    color = CokPalette.dim, fontSize = 12.sp,
                )
            }
        }
        Spacer(Modifier.height(10.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(
                "连消耗项一起(会烧金币/道具/体力)",
                color = CokPalette.dim2, fontSize = 11.sp, modifier = Modifier.weight(1f),
            )
            Switch(checked = costly, onCheckedChange = { onCostlyChange(it) })
        }
        Spacer(Modifier.height(10.dp))
        PrimaryAction(
            label = "一键完成",
            disabled = busy != null,
            modifier = Modifier.fillMaxWidth(),
            loading = busy == "ASSIST",
            onClick = onRun,
        )
        Spacer(Modifier.height(6.dp))
        Text(
            "等同游戏里「领地辅助 → 一键完成」：按面板顺序逐项执行，不用一项项点。" +
                "默认只跑无损项；勾上「连消耗项一起」才连试炼/招募/献祭那些一起跑。",
            color = CokPalette.dim2, fontSize = 10.sp, lineHeight = 15.sp,
        )
    }
}

@Composable
private fun AllianceCard(
    alliance: AllianceStatus?,
    busy: String?,
    onAccept: () -> Unit,
    onDonate: () -> Unit,
    onHelpAll: () -> Unit,
    onSignIn: () -> Unit,
) {
    Column(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(10.dp)).background(CokPalette.surface)
            .border(1.dp, CokPalette.line, RoundedCornerShape(10.dp)).padding(14.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text("联盟", color = CokPalette.fg, fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
                Text(
                    if (alliance == null) "正在读取联盟数据"
                    else "在研科技 ${alliance.researchingScienceId.ifBlank { "无" }}" +
                        " · 任务位 ${alliance.taskAcceptLeft}",
                    color = CokPalette.dim, fontSize = 12.sp,
                )
            }
        }
        if (alliance == null) {
            Spacer(Modifier.height(8.dp))
            Text("尚未读到联盟数据（等待控制台读取联盟面板）", color = CokPalette.dim2, fontSize = 11.sp)
            return@Column
        }
        Spacer(Modifier.height(8.dp))
        if (alliance.researchingScienceId.isNotBlank()) {
            Text(
                "科技 ${alliance.researchingScienceId} · 等级 ${alliance.researchingLevel}" +
                    " · 星级 ${alliance.researchingStar} · 进度 ${alliance.researchingProgress}" +
                    " (${alliance.researchingPercent}%)",
                color = CokPalette.dim2, fontSize = 11.sp,
            )
        }
        alliance.donateTiers.forEach { tier ->
            val mark = when (tier.available) {
                true -> "可捐"
                false -> "不可捐"
                null -> "默认"
            }
            Text(
                "${tier.name} · ${tier.resource} ×${tier.amount} → 贡献 ${tier.contribute}" +
                    " / 进度 ${tier.progress} · $mark",
                color = CokPalette.dim2, fontSize = 11.sp,
            )
        }
        if (alliance.donateReason.isNotBlank()) {
            Spacer(Modifier.height(4.dp))
            Text(alliance.donateReason, color = CokPalette.warn, fontSize = 11.sp)
        }
        Spacer(Modifier.height(4.dp))
        Text(
            "联盟签到 ${alliance.signInDays} 天一轮 · " +
                (if (alliance.signInDone) "今日已签" else "今日未签") +
                " · 联盟积分 ${alliance.alliancePoint}",
            color = CokPalette.dim2, fontSize = 11.sp,
        )
        Spacer(Modifier.height(12.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
            SecondaryAction(
                label = "接任务",
                disabled = busy != null || alliance.taskAcceptLeft <= 0,
                modifier = Modifier.weight(1f),
                loading = busy == "ALLIANCE_ACCEPT",
                onClick = onAccept,
            )
            SecondaryAction(
                label = "帮助全体",
                disabled = busy != null,
                modifier = Modifier.weight(1f),
                loading = busy == "ALLIANCE_HELP_ALL",
                onClick = onHelpAll,
            )
        }
        Spacer(Modifier.height(10.dp))
        SecondaryAction(
            label = if (alliance.signInDone) "今日已签到" else "领取联盟签到",
            disabled = busy != null || alliance.signInDone,
            modifier = Modifier.fillMaxWidth(),
            loading = busy == "ALLIANCE_SIGN_IN",
            onClick = onSignIn,
        )
        Spacer(Modifier.height(10.dp))
        PrimaryAction(
            label = "捐献(低档)",
            disabled = busy != null || !alliance.donateReady,
            modifier = Modifier.fillMaxWidth(),
            loading = busy == "ALLIANCE_DONATE",
            onClick = onDonate,
        )
    }
}

@Composable
private fun OperationSection(text: String) = Text(text.uppercase(), color = CokPalette.dim2, fontSize = 11.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.1.sp)

@Composable
private fun PrimaryAction(label: String, disabled: Boolean, modifier: Modifier, loading: Boolean = false, onClick: () -> Unit) = Button(
    onClick = onClick, enabled = !disabled, modifier = modifier, shape = RoundedCornerShape(8.dp),
    colors = ButtonDefaults.buttonColors(containerColor = CokPalette.accent, contentColor = Color.White),
) { LoadingLabel(label, loading, Color.White) }

@Composable
private fun SecondaryAction(
    label: String,
    disabled: Boolean,
    modifier: Modifier,
    loading: Boolean = false,
    onClick: () -> Unit,
) = OutlinedButton(
    onClick = onClick, enabled = !disabled, modifier = modifier, shape = RoundedCornerShape(8.dp),
) { LoadingLabel(label, loading, CokPalette.accentText) }

@Composable
private fun LoadingLabel(label: String, loading: Boolean, color: Color) {
    if (loading) CircularProgressIndicator(Modifier.height(18.dp), color = color, strokeWidth = 2.dp) else Text(label)
}

@Composable
private fun ConfirmDialog(
    title: String,
    body: String,
    confirmLabel: String,
    danger: Boolean = false,
    onDismiss: () -> Unit,
    onConfirm: () -> Unit,
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(title) }, text = { Text(body) },
        confirmButton = {
            Button(
                onClick = onConfirm,
                colors = if (danger) ButtonDefaults.buttonColors(containerColor = CokPalette.err) else ButtonDefaults.buttonColors(),
            ) { Text(confirmLabel) }
        },
        dismissButton = { OutlinedButton(onClick = onDismiss) { Text("取消") } },
    )
}

private fun speedupConfirmation(queue: QueueStatus, item: SpeedupItem, count: Int): String = buildString {
    append("将对“${queue.name} · ${queue.detail}”使用 ${item.name} x$count。")
    item.label.takeIf { it.isNotBlank() }?.let { append("\n\n道具效果：$it") }
    append("\n当前队列剩余 ${formatQueueDuration(queue.remainingMillis)}；提交后会立即消耗道具。")
}

private fun shieldConfirmation(slot: ShieldSlot, item: ShieldItem): String = buildString {
    append("将使用“${slot.name}”中的 ${item.name}")
    item.duration.takeIf { it.isNotBlank() }?.let { append("（$it）") }
    append("开启保护罩。")
    append("\n\n此操作会真实消耗 1 个保护罩道具；如当前已有保护罩，游戏会按槽位规则覆盖或延长。")
}

private fun formatQueueDuration(millis: Long): String {
    val seconds = (millis / 1_000L).coerceAtLeast(0L)
    return when {
        seconds >= 86_400 -> "${seconds / 86_400} 天 ${(seconds % 86_400) / 3_600} 小时"
        seconds >= 3_600 -> "${seconds / 3_600} 小时 ${(seconds % 3_600) / 60} 分"
        seconds >= 60 -> "${seconds / 60} 分"
        else -> "$seconds 秒"
    }
}

private fun huntConfirmation(
    level: Int,
    squads: Int,
    soldiersPerSquad: Int,
    maxKills: Int,
    mix: Int,
    autoStamina: Boolean = false,
): String {
    val limit = if (maxKills == 0) "不限次数，直到你停止或体力不足" else "最多 $maxKills 只"
    val troops = if (mix <= 1) "每队 1 种兵" else "每队最多 $mix 种兵（混编）"
    val potion = if (autoStamina) "\n体力不足时会自动喝背包里的体力药水（会消耗药水）。" else ""
    return "目标等级 $level，$squads 队并行，每队最多 $soldiersPerSquad 人，$troops。$limit。" +
        "\n\n单轮最多消耗约 ${squads * HUNT_STAMINA_COST} 点体力。自动打怪会独占当前账号连接，状态监控会暂时让位；随时可在此停止。" +
        potion
}

private const val HUNT_STAMINA_COST = 9

private fun rallyConfirmation(
    target: RallyTarget?,
    minutes: Int,
    soldiers: Int,
    staminaCost: Int,
): String {
    val where = target?.let { "${it.level} 级巨型狮鹫 · #${it.index}" } ?: "未选择目标"
    return "目标：$where\n集结等待：$minutes 分钟\n派兵：$soldiers 人\n\n" +
        "真实消耗约 $staminaCost 点体力与所派士兵，并在联盟里建一个集结（其他成员可以加入）。" +
        "同一目标只能有一支集结，打完才能再发。"
}

private const val SAFETY_SECTION_INDEX = 4
private const val HUNT_SECTION_INDEX = 7
