package com.cok.console.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.cok.console.net.ConsoleRepository
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import org.json.JSONArray
import org.json.JSONObject

/** UI state for the native home screen. */
data class HomeUiState(
    val loading: Boolean = true,
    val refreshing: Boolean = false,
    val snapshot: ConsoleSnapshot? = null,
    val errorMessage: String? = null,
    val actionMessage: String? = null,
    val actionOutcome: ActionOutcome? = null,
    val actionInFlight: QuickAction? = null,
    val locallyResolvedActions: Set<QuickAction> = emptySet(),
    val automationSettingInFlight: String? = null,
    val accountActionInFlight: Boolean = false,
    val channelLoginInFlight: Boolean = false,
    val channelLoginResult: ChannelLoginResult? = null,
    val channelLoginError: String? = null,
    val channelAddInFlight: Boolean = false,
    val operationInFlight: String? = null,
    val scanStatus: MapIndexStatus? = null,
    val scanInFlight: Boolean = false,
    val scanHistory: List<ScanHistoryRun> = emptyList(),
    val locateInFlight: Boolean = false,
    val locateResult: LocateResult? = null,
    val exportInFlight: Boolean = false,
    val exportPayload: ExportPayload? = null,
    val rally: RallyStatus? = null,
    val rallyInFlight: Boolean = false,
)

/**
 * Owns the polling loop and quick-action calls for the native home screen.
 *
 * All state changes still go through the loopback API; this never mutates game
 * state on its own. The Python side keeps enforcing account locks and risk.
 */
class ConsoleViewModel(private val repo: ConsoleRepository) : ViewModel() {

    private val _state = MutableStateFlow(HomeUiState())
    val state = _state.asStateFlow()

    private var pollJob: Job? = null

    fun start() {
        if (pollJob != null) return
        pollJob = viewModelScope.launch {
            while (true) {
                loadOnce(silent = _state.value.snapshot != null)
                // 扫描状态有两个来源:主轮询的 /api/state(map_index.scanning)和独立的
                // /api/scan/status。扫描**自己跑完**时 /api/state 会先翻成 scanning=false,
                // 若此刻就停掉 loadScanStatus(), scanStatus 会卡在最后一次 running=true,
                // 卡片永远显示「扫描中」。只要**任一来源**还说在扫就再拉一次, 收尾那次
                // running=false 才能补上, 卡片才会切回已完成。
                if (_state.value.snapshot?.mapIndex?.isScanning == true ||
                    _state.value.scanStatus?.isScanning == true
                ) {
                    loadScanStatus()
                }
                delay(POLL_INTERVAL_MS)
            }
        }
    }

    fun startScan(step: Int, resume: Boolean) {
        viewModelScope.launch {
            _state.update { it.copy(scanInFlight = true, actionMessage = null) }
            val result = repo.startScan(step, resume)
            val message = result.fold(
                onSuccess = { json ->
                    if (json.optBoolean("ok")) json.optString("note").ifBlank { "扫描已启动" }
                    else "启动扫描失败：${json.optString("error").ifBlank { "未知错误" }}"
                },
                onFailure = { "启动扫描失败：${it.message ?: "网络异常"}" },
            )
            _state.update { it.copy(scanInFlight = false, actionMessage = message) }
            loadScanStatus()
            loadOnce(silent = true)
        }
    }

    fun stopScan() {
        viewModelScope.launch {
            _state.update { it.copy(scanInFlight = true, actionMessage = null) }
            val result = repo.stopScan()
            val message = result.fold(
                onSuccess = { json ->
                    if (json.optBoolean("ok")) json.optString("note").ifBlank { "已停止扫描" }
                    else "停止扫描失败：${json.optString("error").ifBlank { "未知错误" }}"
                },
                onFailure = { "停止扫描失败：${it.message ?: "网络异常"}" },
            )
            _state.update { it.copy(scanInFlight = false, actionMessage = message) }
            loadScanStatus()
            loadOnce(silent = true)
        }
    }

    fun refreshScanStatus() {
        viewModelScope.launch { loadScanStatus() }
    }

    fun locatePlayer(name: String, scanNearby: Boolean) {
        if (name.isBlank() && !scanNearby) {
            _state.update { it.copy(actionMessage = "请输入玩家名称") }
            return
        }
        viewModelScope.launch {
            _state.update { it.copy(locateInFlight = true, locateResult = null, actionMessage = null) }
            val body = JSONObject().put("action", "locate").put("name", name.trim())
            if (scanNearby) body.put("op", "scan")
            val result = repo.action(body)
            result.fold(
                onSuccess = { json ->
                    if (!json.optBoolean("ok")) {
                        _state.update { it.copy(actionMessage = "查询失败：${json.optString("error").ifBlank { json.optString("errorText") }.ifBlank { "未知错误" }}") }
                    } else {
                        val players = json.optJSONArray("players")?.let { array ->
                            buildList {
                                for (index in 0 until array.length()) {
                                    val item = array.optJSONObject(index) ?: continue
                                    val level = item.opt("level")?.toString().orEmpty().takeUnless { it == "null" }.orEmpty()
                                    val x = item.opt("x")?.toString().orEmpty().takeUnless { it == "null" }.orEmpty()
                                    val y = item.opt("y")?.toString().orEmpty().takeUnless { it == "null" }.orEmpty()
                                    add(LocatedPlayer(item.optString("name"), item.optString("uid"), x, y, level))
                                }
                            }
                        }.orEmpty()
                        val source = json.optString("source")
                        val requests = json.optJSONObject("scan")?.optInt("requests") ?: 0
                        val stale = json.optBoolean("stale")
                        val serverMsg = json.optString("message").takeIf { msg -> msg.isNotBlank() }
                        val message = serverMsg ?: if (scanNearby) "附近扫描完成" else "已查到 ${players.size} 个匹配项"
                        _state.update { it.copy(locateResult = LocateResult(source, players, message, requests, stale)) }
                    }
                },
                onFailure = { _state.update { state -> state.copy(actionMessage = "查询失败：${it.message ?: "网络异常"}") } },
            )
            _state.update { it.copy(locateInFlight = false) }
            loadOnce(silent = true)
        }
    }

    fun exportPlayers(playersOnly: Boolean) {
        viewModelScope.launch {
            _state.update { it.copy(exportInFlight = true, exportPayload = null, actionMessage = null) }
            val result = repo.exportPlayers(playersOnly)
            result.fold(
                onSuccess = { bytes ->
                    val filename = if (playersOnly) "cok-players-real.xlsx" else "cok-players.xlsx"
                    _state.update { it.copy(exportInFlight = false, exportPayload = ExportPayload(filename, bytes)) }
                },
                onFailure = { error ->
                    _state.update { it.copy(exportInFlight = false, actionMessage = "导出失败：${error.message ?: "未知错误"}") }
                },
            )
        }
    }

    fun markExportSaved(message: String) {
        _state.update { it.copy(exportPayload = null, actionMessage = message) }
    }

    private suspend fun loadScanStatus() {
        repo.fetchScanStatus().onSuccess { json ->
            _state.update {
                it.copy(
                    scanStatus = MapIndexStatus(
                        playerCount = json.optInt("players"),
                        isScanning = json.optBoolean("running"),
                        requestsDone = json.optInt("requests_done"),
                        requestsTotal = json.optInt("requests_total"),
                        percent = json.optDouble("percent").toFloat().coerceIn(0f, 100f),
                        isPartial = json.optBoolean("partial"),
                        errors = json.optInt("errors"),
                        mismatched = json.optInt("mismatched"),
                        dropped = json.optInt("dropped"),
                    ),
                )
            }
        }
        repo.fetchScanHistory().onSuccess { json ->
            val runs = json.optJSONArray("runs")?.let { array ->
                buildList {
                    for (index in 0 until array.length()) {
                        val r = array.optJSONObject(index) ?: continue
                        add(
                            ScanHistoryRun(
                                startedAt = r.optLong("started_at"),
                                finishedAt = r.optLong("finished_at"),
                                status = r.optString("status"),
                                step = r.optInt("step"),
                                radius = r.optInt("radius"),
                                players = r.optInt("players"),
                                realPlayers = r.optInt("real_players"),
                                requestsDone = r.optInt("requests_done"),
                                requestsTotal = r.optInt("requests_total"),
                                errors = r.optInt("errors"),
                            ),
                        )
                    }
                }
            }.orEmpty()
            _state.update { it.copy(scanHistory = runs) }
        }
    }

    fun refresh() {
        viewModelScope.launch {
            _state.update { it.copy(refreshing = true) }
            // Ask the server to poll the game now, then re-read the snapshot.
            val result = repo.action(JSONObject().put("action", "refresh-now"))
            val message = result.fold(
                onSuccess = { json ->
                    if (actionSucceeded(json)) null else {
                        "刷新失败：${json.optString("error")
                            .ifBlank { json.optString("note") }
                            .ifBlank { "未知错误" }}"
                    }
                },
                onFailure = { "刷新失败：${it.message ?: "网络异常"}" },
            )
            loadOnce(silent = true)
            _state.update { it.copy(refreshing = false, actionMessage = message ?: it.actionMessage) }
        }
    }

    private suspend fun loadOnce(silent: Boolean): Boolean {
        if (!silent) _state.update { it.copy(loading = true) }
        return repo.fetchState().fold(
            onSuccess = { json ->
                if (json.optString("error") == "unauthorized") {
                    _state.update { it.copy(loading = false, errorMessage = "token 无效") }
                    false
                } else {
                    val parsed = ConsoleSnapshot.from(json)
                    _state.update {
                        val stillPending = parsed.triage.mapNotNull { it.action }.toSet()
                        it.copy(
                            loading = false,
                            snapshot = parsed,
                            errorMessage = null,
                            // Once a freshly-read game snapshot no longer contains the
                            // task, release the optimistic completion mask. If it later
                            // becomes actionable again it will appear normally.
                            locallyResolvedActions = it.locallyResolvedActions.intersect(stillPending),
                        )
                    }
                    true
                }
            },
            onFailure = { err ->
                _state.update {
                    it.copy(
                        loading = false,
                        errorMessage = err.message ?: "控制台无响应",
                    )
                }
                false
            },
        )
    }

    fun runAction(action: QuickAction) {
        viewModelScope.launch {
            if (_state.value.actionInFlight != null || _state.value.operationInFlight != null) return@launch
            if (action.requiresConfirm && _state.value.snapshot?.gameDataAvailable != true) {
                _state.update { it.copy(actionMessage = "尚未读取当前游戏数据，请刷新后再试") }
                return@launch
            }
            _state.update {
                it.copy(
                    actionInFlight = action,
                    actionMessage = null,
                    actionOutcome = ActionOutcome(action.actionLabel, "正在提交到游戏…", succeeded = true, snapshotVerified = false),
                )
            }
            val body = bodyFor(action)
            val result = repo.action(body)
            val succeeded = result.getOrNull()?.let(::actionSucceeded) == true
            val message = result.fold(
                onSuccess = { summarize(action, it) },
                onFailure = { "操作失败：${it.message ?: "未知错误"}" },
            )
            // A successful game response is enough to remove a routine item in
            // the current frame. The follow-up poll is verification, not a
            // prerequisite for the UI to feel complete.
            if (succeeded && action != QuickAction.REFRESH) {
                _state.update {
                    it.copy(
                        locallyResolvedActions = it.locallyResolvedActions + action,
                        actionOutcome = ActionOutcome(
                            action.actionLabel,
                            "$message，正在用游戏状态确认…",
                            succeeded = true,
                            snapshotVerified = false,
                        ),
                    )
                }
            }
            // Action responses update only their own result. Re-poll after a
            // confirmed game action so the next snapshot remains authoritative.
            val refreshed = if (succeeded && action != QuickAction.REFRESH) {
                refreshSnapshotAfterAction()
            } else {
                loadOnce(silent = true)
            }
            publishOutcome(action.actionLabel, message, succeeded, refreshed)
            _state.update {
                it.copy(
                    actionInFlight = null,
                    actionMessage = message,
                )
            }
        }
    }

    private suspend fun refreshSnapshotAfterAction(): Boolean {
        val poll = repo.action(JSONObject().put("action", "refresh-now"))
        return poll.getOrNull()?.let(::actionSucceeded) == true && loadOnce(silent = true)
    }

    private fun actionSucceeded(json: JSONObject): Boolean =
        !json.has("ok") || json.optBoolean("ok", true)

    fun clearActionMessage() {
        _state.update { it.copy(actionMessage = null) }
    }

    fun clearActionOutcome() {
        _state.update { it.copy(actionOutcome = null) }
    }

    fun switchAccount(key: String) = runAccountAction("切换账号") {
        JSONObject().put("action", "account-switch").put("key", key)
    }

    fun setAccountParallel(key: String, enabled: Boolean) = runAccountAction(
        if (enabled) "已开启后台运行" else "已停止后台运行",
    ) {
        JSONObject().put("action", "account-parallel").put("key", key).put("on", enabled)
    }

    fun setAccountsParallel(keys: List<String>, enabled: Boolean) = runAccountAction(
        if (enabled) "已开启所选账号的后台运行" else "已停止所选账号的后台运行",
    ) {
        JSONObject().put("action", "account-parallel-batch").put("keys", keys).put("on", enabled)
    }

    fun importDeviceAccounts() = runAccountAction("已从设备导入账号") {
        JSONObject().put("action", "account-add-device")
    }

    fun renameAccount(key: String, label: String) = runAccountAction("账号名称已更新") {
        JSONObject().put("action", "account-relabel").put("key", key).put("label", label)
    }

    fun removeAccount(key: String) = runAccountAction("账号已从管理中心移除") {
        JSONObject().put("action", "account-remove").put("key", key)
    }

    /** Password is used only for this loopback request and is never retained in UI state. */
    fun loginChannelAccount(account: String, password: String) {
        if (account.isBlank() || password.isBlank()) {
            _state.update { it.copy(channelLoginError = "请填写果盘账号和密码") }
            return
        }
        viewModelScope.launch {
            if (_state.value.channelLoginInFlight || _state.value.channelAddInFlight) return@launch
            _state.update { it.copy(channelLoginInFlight = true, channelLoginError = null, channelLoginResult = null) }
            val response = repo.action(
                JSONObject().put("action", "channel-login").put("account", account.trim()).put("password", password),
            )
            response.fold(
                onSuccess = { json ->
                    when {
                        !json.optBoolean("ok", false) -> _state.update {
                            it.copy(channelLoginError = json.optString("error").ifBlank { "登录请求失败" })
                        }
                        !json.optBoolean("succeeded", false) -> _state.update {
                            it.copy(channelLoginError = json.optString("note").ifBlank { "果盘账号或密码未通过验证" })
                        }
                        else -> _state.update {
                            it.copy(
                                channelLoginResult = ChannelLoginResult(
                                    sessionId = json.optString("sessionId"),
                                    account = json.optString("account"),
                                    guopanUid = json.optString("guopanUid"),
                                    note = json.optString("note"),
                                    smallAccounts = json.optJSONArray("smallAccounts").toChannelGameAccounts(),
                                ),
                            )
                        }
                    }
                },
                onFailure = { error -> _state.update { it.copy(channelLoginError = "登录请求失败：${error.message ?: "网络异常"}") } },
            )
            _state.update { it.copy(channelLoginInFlight = false) }
        }
    }

    fun addChannelAccounts(sessionId: String, perGameIds: List<String>) {
        if (sessionId.isBlank() || perGameIds.isEmpty()) {
            _state.update { it.copy(channelLoginError = "请先选择要加入的游戏号") }
            return
        }
        viewModelScope.launch {
            if (_state.value.channelLoginInFlight || _state.value.channelAddInFlight) return@launch
            _state.update { it.copy(channelAddInFlight = true, channelLoginError = null) }
            val response = repo.action(
                JSONObject().put("action", "channel-add").put("sessionId", sessionId)
                    .put("perGameIds", JSONArray(perGameIds)),
            )
            val message = response.fold(
                onSuccess = { json ->
                    if (!json.optBoolean("ok", false)) {
                        _state.update { it.copy(channelLoginError = json.optString("error").ifBlank { "添加失败" }) }
                        null
                    } else {
                        val labels = buildList {
                            val added = json.optJSONArray("added")
                            for (index in 0 until (added?.length() ?: 0)) {
                                added?.optJSONObject(index)?.optString("label")?.takeIf { it.isNotBlank() }?.let(::add)
                            }
                        }
                        "已加入账号库${if (labels.isEmpty()) "" else "：${labels.joinToString("、")}"}"
                    }
                },
                onFailure = { error ->
                    _state.update { it.copy(channelLoginError = "添加失败：${error.message ?: "网络异常"}") }
                    null
                },
            )
            _state.update {
                it.copy(
                    channelAddInFlight = false,
                    channelLoginResult = if (message != null) null else it.channelLoginResult,
                    actionMessage = message ?: it.actionMessage,
                )
            }
            if (message != null) {
                // channel-add returns once storage and account switching are
                // complete; the server starts its first game sync in background.
                // Read immediately so the UI reflects "syncing" instead of the
                // old empty-account idle state, then the normal poll follows it.
                loadOnce(silent = true)
            }
        }
    }

    fun clearChannelLogin() {
        _state.update { it.copy(channelLoginResult = null, channelLoginError = null) }
    }

    private fun JSONArray?.toChannelGameAccounts(): List<ChannelGameAccount> = buildList {
        for (index in 0 until (this@toChannelGameAccounts?.length() ?: 0)) {
            val item = this@toChannelGameAccounts?.optJSONObject(index) ?: continue
            add(
                ChannelGameAccount(
                    perGameId = item.optString("perGameId"),
                    name = item.optString("name"),
                    roleName = item.optString("roleName"),
                    gameUid = item.optString("gameUid"),
                    zone = item.optString("zn"),
                    level = item.opt("gameUserLevel")?.toString().orEmpty().takeUnless { it == "null" }.orEmpty(),
                    hasCharacter = item.optBoolean("hasCharacter"),
                    inLibrary = item.optBoolean("inLibrary"),
                    note = item.optString("note"),
                ),
            )
        }
    }

    fun setAutomationSetting(key: String, enabled: Boolean, label: String) {
        viewModelScope.launch {
            if (_state.value.automationSettingInFlight != null) return@launch
            _state.update { it.copy(automationSettingInFlight = key, actionMessage = null) }
            val result = repo.action(
                JSONObject().put("action", "set-setting").put("key", key).put("value", enabled),
            )
            val message = result.fold(
                onSuccess = { json ->
                    if (json.optBoolean("ok")) "已${if (enabled) "开启" else "关闭"}$label"
                    else "保存失败：${json.optString("error").ifBlank { "未知错误" }}"
                },
                onFailure = { "保存失败：${it.message ?: "网络异常"}" },
            )
            _state.update { it.copy(automationSettingInFlight = null, actionMessage = message) }
            loadOnce(silent = true)
        }
    }

    fun saveHuntPlan(
        level: Int,
        soldiersPerSquad: Int,
        squads: Int,
        maxKills: Int,
        mix: Int = 1,
        autoStamina: Boolean = false,
    ) = saveSetting(
        inFlightKey = "hunt-plan",
        settings = listOf(
            "lvLow" to level.coerceIn(1, 30),
            "lvHigh" to level.coerceIn(1, 30),
            "perType" to soldiersPerSquad.coerceIn(1, 999_999),
            "squads" to squads.coerceIn(1, 8),
            "huntMax" to maxKills.coerceIn(0, 500),
            // 每队最多几种兵: 1 = 单兵种; 2+ = 一次出征混编多个同类兵种
            "huntMix" to mix.coerceIn(1, 4),
            // 体力不足时自动喝背包里的体力药水
            "huntAutoStamina" to autoStamina,
        ),
        successMessage = "已保存默认打怪方案",
    )

    private fun saveSetting(
        inFlightKey: String,
        settings: List<Pair<String, Any>>,
        successMessage: String,
    ) {
        viewModelScope.launch {
            if (_state.value.automationSettingInFlight != null) return@launch
            _state.update { it.copy(automationSettingInFlight = inFlightKey, actionMessage = null) }
            val failed = settings.firstNotNullOfOrNull { (key, value) ->
                repo.action(JSONObject().put("action", "set-setting").put("key", key).put("value", value))
                    .fold(
                        onSuccess = { json -> if (json.optBoolean("ok")) null else json.optString("error").ifBlank { "未知错误" } },
                        onFailure = { it.message ?: "网络异常" },
                    )
            }
            _state.update {
                it.copy(
                    automationSettingInFlight = null,
                    actionMessage = failed?.let { reason -> "保存失败：$reason" } ?: successMessage,
                )
            }
            loadOnce(silent = true)
        }
    }

    fun setAutoShield(enabled: Boolean) =
        setAutomationSetting("autoShield", enabled, "被攻击自动保护")

    fun saveAutomationPolicy(
        paused: Boolean,
        mode: String,
        maxFailures: Int,
        backoffMinutes: Int,
        alertLevel: String,
        huntMinStamina: Int,
        skyMinPower: Int,
        dockMinResourceReserve: Int,
    ) = saveSetting(
        inFlightKey = "automation-policy",
        settings = listOf(
            "automationPaused" to paused,
            "automationMode" to mode,
            "automationMaxFailures" to maxFailures.coerceIn(1, 120),
            "automationBackoffMinutes" to backoffMinutes.coerceIn(1, 120),
            "automationAlertLevel" to alertLevel,
            "huntMinStamina" to huntMinStamina.coerceAtLeast(0),
            "skyMinPower" to skyMinPower.coerceAtLeast(0),
            "dockMinResourceReserve" to dockMinResourceReserve.coerceAtLeast(0),
        ),
        successMessage = if (paused) "已暂停全部自动化" else "自动化安全策略已保存",
    )

    fun recheckAutomation(key: String) = runOperation(
        id = "automation-recheck-$key",
        successMessage = "已请求重新检查",
        verifyWithRefresh = false,
    ) {
        JSONObject().put("action", "automation-recheck").put("key", key)
    }

    fun setAccountPriority(key: String, priority: Int) = runAccountAction("账号调度优先级已更新") {
        JSONObject().put("action", "account-priority").put("key", key).put("priority", priority.coerceIn(1, 3))
    }

    fun useShield(slot: ShieldSlot, item: ShieldItem) = runOperation(
        "shield-use", "已提交开启保护罩",
        requiresGameData = true,
    ) {
        JSONObject().put("action", "shield").put("slot", slot.index)
            .put("coverOld", 1).put("spec", item.id)
    }

    fun startHunt(
        level: Int,
        soldiersPerSquad: Int,
        squads: Int,
        maxKills: Int,
        mix: Int = 1,
        autoStamina: Boolean = false,
    ) = runOperation(
        "hunt-start", "已开始自动打怪",
        requiresGameData = true, requiresHuntData = true,
    ) {
        JSONObject().put("action", "hunt").put("op", "auto-start")
            .put("level", level).put("num", soldiersPerSquad)
            .put("squads", squads).put("maxKills", maxKills)
            // 每队最多几种兵(1=单兵种; 2+=一次出征带多个同类兵种)
            .put("mix", mix.coerceIn(1, 4))
            // 体力不足时自动喝背包里的体力药水
            .put("autoStamina", autoStamina)
    }

    fun stopHunt() = runOperation("hunt-stop", "已停止自动打怪", requiresGameData = true) {
        JSONObject().put("action", "hunt").put("op", "auto-stop")
    }

    /**
     * Read the giant-griffin rally state (duration tiers, known targets, my rallies).
     *
     * This is a separate operation instead of part of /api/state because it has to
     * pull map tiles with world.get, which is far too slow for the main poll.
     */
    fun loadRally(force: Boolean = false) {
        if (_state.value.rallyInFlight) return
        viewModelScope.launch {
            _state.update { it.copy(rallyInFlight = true) }
            val body = JSONObject().put("action", "hunt").put("op", "rally-state")
            if (force) body.put("force", true)
            val result = repo.action(body)
            result.fold(
                onSuccess = { json ->
                    val parsed = parseRally(json)
                    _state.update { it.copy(rally = parsed, rallyInFlight = false) }
                },
                onFailure = { error ->
                    _state.update {
                        it.copy(
                            rallyInFlight = false,
                            actionMessage = "读取集结状态失败：${error.message ?: "网络异常"}",
                        )
                    }
                },
            )
        }
    }

    /** Start a rally on the chosen target. Real cost: stamina, soldiers, alliance team. */
    fun startRally(index: Int, slot: Int, num: Int) = runOperation(
        "rally-start", "已发起集结", verifyWithRefresh = false, after = { loadRally() },
    ) {
        JSONObject().put("action", "hunt").put("op", "rally-start")
            .put("index", index).put("slot", slot).put("num", num)
    }

    private fun parseRally(json: JSONObject): RallyStatus {
        val slots = buildList {
            val array = json.optJSONArray("slots")
            for (index in 0 until (array?.length() ?: 0)) {
                val item = array?.optJSONObject(index) ?: continue
                add(RallySlot(item.optInt("slot", 1), item.optInt("minutes", 0)))
            }
        }
        val bosses = buildList {
            val array = json.optJSONArray("bosses")
            for (index in 0 until (array?.length() ?: 0)) {
                val item = array?.optJSONObject(index) ?: continue
                add(
                    RallyTarget(
                        index = item.optInt("index"),
                        monsterId = item.optString("monsterId"),
                        level = item.optInt("level"),
                        hp = item.optInt("hp"),
                        maxHp = item.optInt("maxHp"),
                        busy = item.optBoolean("busy"),
                    )
                )
            }
        }
        val mine = buildList {
            val array = json.optJSONArray("my_rallies")
            for (index in 0 until (array?.length() ?: 0)) {
                val item = array?.optJSONObject(index) ?: continue
                add(
                    RallyMine(
                        targetId = item.optInt("targetId"),
                        monsterId = item.optString("monsterId"),
                        waitMinutes = item.optDouble("wait_minutes", 0.0),
                        members = item.optInt("members"),
                    )
                )
            }
        }
        return RallyStatus(
            loaded = json.optBoolean("ok"),
            levels = bosses.map { it.level }.filter { it > 0 }.distinct().sorted(),
            bosses = bosses,
            slots = slots,
            myRallies = mine,
            rallyCount = json.optInt("rally_count"),
            known = json.optJSONObject("scan")?.optInt("known") ?: bosses.size,
            stamina = json.optInt("stamina"),
            staminaCost = json.optInt("stamina_cost", 20),
        )
    }

    fun speedUpWithItem(queue: QueueStatus, item: SpeedupItem, count: Int) = runOperation(
        "speedup-item", "已提交道具加速",
        requiresGameData = true,
    ) {
        JSONObject().put("action", "speedup").put("uuid", queue.uuid)
            .put("itemUuid", item.uuid).put("count", count.coerceIn(1, item.count))
    }

    fun speedUpWithGold(queue: QueueStatus) = runOperation("speedup-gold", "已提交金币加速", requiresGameData = true) {
        JSONObject().put("action", "speedup").put("uuid", queue.uuid)
            // The verified gold recipe uses queueType=1 on this console path;
            // QueueStatus.type is the display/category value from the snapshot.
            .put("gold", true).put("qid", queue.queueId).put("qtype", 1)
    }

    fun reconnect() = runOperation(
        id = "reconnect",
        successMessage = "已完成重新连接",
        // Reconnect validates the game session. A full snapshot follows through
        // the normal poll loop, so do not turn a successful handshake into an
        // apparent timeout by immediately waiting for every optional module.
        verifyWithRefresh = false,
    ) {
        JSONObject().put("action", "reconnect")
    }

    fun disconnect() = runOperation(
        id = "disconnect",
        successMessage = "已断开连接",
        verifyWithRefresh = false,
    ) {
        JSONObject().put("action", "disconnect")
    }

    fun claimSkyReward() = runOperation("sky-reward", "已领取探索奖励", requiresGameData = true) {
        JSONObject().put("action", "sky").put("op", "reward")
    }

    fun startSkyExplore() = runOperation("sky-explore", "已开始探索", requiresGameData = true) {
        JSONObject().put("action", "sky").put("op", "explore")
    }

    private fun runAccountAction(successMessage: String, body: () -> JSONObject) {
        viewModelScope.launch {
            if (_state.value.accountActionInFlight) return@launch
            _state.update { it.copy(accountActionInFlight = true, actionMessage = null) }
            val result = repo.action(body())
            val message = result.fold(
                onSuccess = { json ->
                    if (json.optBoolean("ok", false)) successMessage
                    else "操作失败：${json.optString("error").ifBlank { "未知错误" }}"
                },
                onFailure = { "操作失败：${it.message ?: "未知错误"}" },
            )
            _state.update { it.copy(accountActionInFlight = false, actionMessage = message) }
            loadOnce(silent = true)
        }
    }

    private fun runOperation(
        id: String,
        successMessage: String,
        requiresGameData: Boolean = false,
        requiresHuntData: Boolean = false,
        verifyWithRefresh: Boolean = true,
        after: () -> Unit = {},
        body: () -> JSONObject,
    ) {
        viewModelScope.launch {
            if (_state.value.operationInFlight != null || _state.value.actionInFlight != null) return@launch
            if (requiresGameData && _state.value.snapshot?.gameDataAvailable != true) {
                _state.update { it.copy(actionMessage = "尚未读取当前游戏数据，请刷新后再试") }
                return@launch
            }
            if (requiresHuntData && _state.value.snapshot?.operations?.huntDataAvailable != true) {
                _state.update { it.copy(actionMessage = "体力与打怪配置尚未同步，请刷新后再试") }
                return@launch
            }
            _state.update {
                it.copy(
                    operationInFlight = id,
                    actionMessage = null,
                    actionOutcome = ActionOutcome(successMessage, "正在提交到游戏…", succeeded = true, snapshotVerified = false),
                )
            }
            val result = repo.action(body())
            val succeeded = result.getOrNull()?.let(::actionSucceeded) == true
            val message = result.fold(
                onSuccess = { json ->
                    if (json.optBoolean("ok", true)) json.optString("note").ifBlank { successMessage }
                    else "操作失败：${json.optString("error")
                        .ifBlank { json.optString("errorText") }
                        .ifBlank { json.optString("hint") }
                        .ifBlank { json.optString("note") }
                        .ifBlank { "未知错误" }}"
                },
                onFailure = { "操作失败：${it.message ?: "未知错误"}" },
            )
            val refreshed = when {
                !succeeded -> loadOnce(silent = true)
                verifyWithRefresh -> refreshSnapshotAfterAction()
                else -> loadOnce(silent = true)
            }
            publishOutcome(successMessage, message, succeeded, refreshed)
            _state.update { it.copy(operationInFlight = null, actionMessage = message) }
            after()
        }
    }

    private fun publishOutcome(title: String, message: String, succeeded: Boolean, refreshed: Boolean) {
        val pending = _state.value.snapshot?.pendingCount
        val detail = when {
            !succeeded -> message
            refreshed -> "$message · 状态已刷新确认${pending?.let { " · 当前 $it 项待办" }.orEmpty()}"
            else -> "$message · 未能完成状态刷新，请稍后手动刷新确认"
        }
        _state.update {
            it.copy(
                actionOutcome = ActionOutcome(title, detail, succeeded, refreshed, pending),
            )
        }
    }

    /** 「一键完成」是否连消耗项一起跑(会烧金币/道具/体力)。 */
    @Volatile
    var costlyAssist: Boolean = false

    private fun bodyFor(action: QuickAction): JSONObject = when (action) {
        QuickAction.REFRESH -> JSONObject().put("action", "refresh-now")
        QuickAction.ASSIST -> JSONObject().put("action", "assist-onekey")
            .put("costly", costlyAssist)
        QuickAction.SIGN -> JSONObject().put("action", "sign")
        QuickAction.CLAIM -> JSONObject().put("action", "claim")
        QuickAction.WELFARE_CLAIM -> JSONObject().put("action", "welfare").put("op", "claim")
        QuickAction.DOCK_REWARD -> JSONObject().put("action", "dock").put("op", "reward")
        QuickAction.ALLIANCE_ACCEPT -> JSONObject().put("action", "alliance").put("op", "accept-all")
        QuickAction.ALLIANCE_DONATE -> JSONObject().put("action", "alliance").put("op", "donate")
            .put("tier", "low")
        QuickAction.ALLIANCE_HELP_ALL -> JSONObject().put("action", "alliance").put("op", "help-all")
        QuickAction.ALLIANCE_SIGN_IN -> JSONObject().put("action", "alliance").put("op", "sign-in")
    }

    private fun summarize(action: QuickAction, json: JSONObject): String {
        val ok = !json.has("ok") || json.optBoolean("ok", true)
        if (!ok) {
            val why = json.optString("error").ifBlank { json.optString("note") }.ifBlank { "未成功" }
            return "${action.actionLabel}失败：$why"
        }
        return when (action) {
            QuickAction.ASSIST -> {
                val changed = json.optBoolean("changed")
                if (changed) "已收取领地资源" else "暂时没有可收取的领地资源"
            }
            QuickAction.WELFARE_CLAIM -> {
                val acted = json.optJSONArray("acted")
                if (acted != null && acted.length() > 0) "已领取 ${acted.length()} 项福利"
                else "没有可领取的福利"
            }
            QuickAction.DOCK_REWARD -> {
                val rewards = json.optJSONArray("rewards")
                val count = rewards?.length() ?: json.optInt("count", 0)
                if (count > 0) "已领取 $count 条港口奖励" else "没有可领取的港口奖励"
            }
            QuickAction.ALLIANCE_ACCEPT -> {
                val result = json.optJSONObject("result")
                val acted = result?.optJSONArray("acted")
                if (acted != null && acted.length() > 0) "已接取 ${acted.length()} 个联盟任务"
                else "没有可接取的联盟任务"
            }
            QuickAction.ALLIANCE_DONATE -> "已捐献联盟科技"
            QuickAction.ALLIANCE_HELP_ALL -> "已帮助联盟全体"
            QuickAction.ALLIANCE_SIGN_IN -> {
                val result = json.optJSONObject("result")
                if (result != null && result.optBoolean("already")) "今天已经签过了"
                else "联盟签到成功"
            }
            else -> {
                val note = json.optString("note")
                if (note.isNotBlank()) "${action.actionLabel}成功 · $note" else "${action.actionLabel}成功"
            }
        }
    }

    private companion object {
        const val POLL_INTERVAL_MS = 8000L
    }
}
