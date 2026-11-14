package com.cok.console.ui

import org.json.JSONObject

/**
 * Turns the raw loopback snapshot into a native, triage-first view model.
 *
 * The parsing mirrors the semantics the web page already uses (same fields, same
 * "this is not an error" special cases), but reshapes it for a mobile home
 * screen: what needs attention first, then compact status, then context.
 */
internal object SnapshotParser {

    fun parse(json: JSONObject): ConsoleSnapshot {
        val states = json.optJSONObject("states") ?: JSONObject()
        val dock = json.optJSONObject("dock") ?: JSONObject()
        val hunter = json.optJSONObject("hunter") ?: JSONObject()
        val hunt = json.optJSONObject("hunt") ?: JSONObject()
        val shield = json.optJSONObject("shield") ?: JSONObject()
        val welfare = json.optJSONObject("welfare") ?: JSONObject()
        val accounts = json.optJSONObject("accounts") ?: JSONObject()

        val (connLabel, connSeverity) = connection(json, hunter)
        val alliance = json.optJSONObject("alliance") ?: JSONObject()
        val triage = triage(states, dock, hunter, hunt, shield, welfare, alliance, json)
        val taskStats = taskStats(json.optJSONObject("task_stats") ?: JSONObject())
        val metrics = metrics(states, dock, hunter, hunt, shield, welfare, json)
        val dashboardCards = dashboardCards(states, json)
        val events = recentEvents(json)
        val operations = operations(json, hunt, hunter, shield, events)
        val mapIndex = mapIndex(json.optJSONObject("map_index") ?: JSONObject())
        val (banner, bannerErr) = banner(json)

        return ConsoleSnapshot(
            connectionLabel = connLabel,
            connectionSeverity = connSeverity,
            gameDataAvailable = json.optBoolean("has_data"),
            account = accountLabel(accounts),
            accounts = accounts(accounts),
            accountSource = json.optString("account_source"),
            lastPoll = lastPoll(json),
            dataIsStale = isDataStale(json),
            triage = triage,
            taskStats = taskStats,
            metrics = metrics,
            dashboardCards = dashboardCards,
            recentEvents = events,
            operations = operations,
            mapIndex = mapIndex,
            bannerText = banner,
            bannerIsError = bannerErr,
        )
    }

    private fun taskStats(stats: JSONObject): TaskStats {
        val periods = stats.optJSONObject("periods") ?: JSONObject()
        fun period(name: String): TaskStatPeriod {
            val raw = periods.optJSONObject(name) ?: JSONObject()
            val entries = raw.optJSONArray("breakdown")?.let { rows ->
                buildList {
                    for (index in 0 until rows.length()) {
                        val row = rows.optJSONObject(index) ?: continue
                        val details = row.optJSONArray("details")?.let { values ->
                            buildList {
                                for (detailIndex in 0 until values.length()) {
                                    val detail = values.optJSONObject(detailIndex) ?: continue
                                    val label = detail.optString("label").trim()
                                    if (label.isNotBlank()) add(TaskStatDetail(label, detail.optInt("count").coerceAtLeast(0)))
                                }
                            }
                        }.orEmpty()
                        val label = row.optString("label").trim()
                        if (label.isNotBlank()) add(TaskStatEntry(label, row.optInt("count").coerceAtLeast(0), details))
                    }
                }
            }.orEmpty()
            return TaskStatPeriod(raw.optString("label").ifBlank { "-" }, raw.optInt("total").coerceAtLeast(0), entries)
        }
        return TaskStats(day = period("day"), week = period("week"), month = period("month"))
    }

    private fun connection(json: JSONObject, hunter: JSONObject): Pair<String, Severity> = when {
        text(json, "account_error").isNotBlank() -> "设备未连接" to Severity.RISK
        json.optBoolean("disconnected") -> "已断开 · 可重连" to Severity.ATTENTION
        hunter.optBoolean("running") -> "自动打怪中" to Severity.OK
        text(json, "error").isNotBlank() -> "连接异常" to Severity.RISK
        json.optBoolean("connected") && !json.optBoolean("has_data") &&
            json.optString("phase") in setOf("启动中", "正在同步") -> "已连接 · 正在同步" to Severity.OK
        json.optBoolean("connected") || json.optBoolean("has_data") -> "已连接" to Severity.OK
        json.optString("phase") in setOf("启动中", "正在同步") -> "正在同步游戏状态" to Severity.INFO
        json.optBoolean("app_yield") -> "App 在线 · 已让出账号" to Severity.INFO
        else -> "空闲" to Severity.INFO
    }

    private fun accountLabel(accounts: JSONObject): String {
        val active = accounts.optString("active").ifBlank { accounts.optString("current") }
        val list = accounts.optJSONArray("list")
        if (list != null) {
            for (i in 0 until list.length()) {
                val a = list.optJSONObject(i) ?: continue
                if (a.optString("key") == active) {
                    return a.optString("label").ifBlank { active }.ifBlank { "未入库账号" }
                }
            }
        }
        return active.ifBlank { "未入库账号" }
    }

    private fun accounts(accounts: JSONObject): List<AccountProfile> {
        val active = accounts.optString("active").ifBlank { accounts.optString("current") }
        val list = accounts.optJSONArray("list") ?: return emptyList()
        return buildList {
            for (index in 0 until list.length()) {
                val item = list.optJSONObject(index) ?: continue
                val key = item.optString("key")
                if (key.isBlank()) continue
                add(
                    AccountProfile(
                        key = key,
                        label = item.optString("label").ifBlank { key },
                        roleName = item.optString("roleName"),
                        gameUid = item.optString("gameUid").ifBlank { key },
                        server = item.optString("zn"),
                        isActive = key == active,
                        isRunning = item.optBoolean("running"),
                        isParallel = item.optBoolean("parallel"),
                    priority = item.optInt("priority", 2).coerceIn(1, 3),
                    automationEnabled = item.optJSONObject("automation")?.optInt("enabled") ?: 0,
                    automationPaused = item.optJSONObject("automation")?.optBoolean("paused") == true,
                    lastAutomationStatus = item.optJSONObject("automation")?.optString("last_status").orEmpty().ifBlank { "waiting" },
                    lastAutomationSummary = item.optJSONObject("automation")?.optString("last_summary").orEmpty().ifBlank { "尚未执行" },
                    summary = item.optJSONObject("summary")?.let { s ->
                        AccountSummary(
                            hasShield = s.optBoolean("has_shield"),
                            shieldMs = s.optLong("shield_ms"),
                            dockRewardable = s.optInt("dock_rewardable"),
                            welfareClaimable = s.optBoolean("welfare_claimable"),
                            hunting = s.optBoolean("hunting"),
                            huntKills = s.optInt("hunt_kills"),
                            error = s.optString("error")
                                .takeUnless { it.isBlank() || it.equals("null", ignoreCase = true) }
                                .orEmpty(),
                            disconnected = s.optBoolean("disconnected"),
                            appYield = s.optBoolean("app_yield"),
                            stale = s.optBoolean("stale"),
                        )
                    },
                    ),
                )
            }
        }
    }

    private fun lastPoll(json: JSONObject): String {
        val poll = json.optDouble("last_poll", 0.0)
        if (poll <= 0.0) return "尚未获得游戏数据"
        val ageSeconds = (System.currentTimeMillis() / 1000L - poll.toLong()).coerceAtLeast(0L)
        return when {
            ageSeconds < 10 -> "刚刚刷新"
            ageSeconds < 60 -> "${ageSeconds} 秒前刷新"
            ageSeconds < 3600 -> "${ageSeconds / 60} 分钟前刷新"
            else -> "${ageSeconds / 3600} 小时前刷新"
        }
    }

    private fun isDataStale(json: JSONObject): Boolean {
        val poll = json.optDouble("last_poll", 0.0)
        val ageSeconds = poll.takeIf { it > 0.0 }
            ?.let { (System.currentTimeMillis() / 1000L - it.toLong()).coerceAtLeast(0L) }
        return TriagePolicy.isStale(ageSeconds)
    }

    private fun triage(
        states: JSONObject,
        dock: JSONObject,
        hunter: JSONObject,
        hunt: JSONObject,
        shield: JSONObject,
        welfare: JSONObject,
        alliance: JSONObject,
        json: JSONObject,
    ): List<TriageItem> {
        val out = mutableListOf<TriageItem>()
        val now = System.currentTimeMillis()
        val lastPoll = json.optDouble("last_poll", 0.0)
        val dataAgeSeconds = if (lastPoll > 0.0) {
            (now / 1000L - lastPoll.toLong()).coerceAtLeast(0L)
        } else {
            null
        }

        when {
            text(json, "account_error").isNotBlank() -> out += TriageItem(
                "设备账号不可用",
                "${text(json, "account_error")}，请检查设备连接后刷新",
                Severity.RISK,
                destination = TriageDestination.MORE,
            )
            json.optBoolean("disconnected") -> out += TriageItem(
                "游戏连接已断开", "可在更多页重新连接", Severity.RISK,
                destination = TriageDestination.MORE,
            )
            text(json, "error").isNotBlank() && !hunter.optBoolean("running") -> out += TriageItem(
                "控制台连接异常", text(json, "error"), Severity.RISK,
                destination = TriageDestination.MORE,
            )
        }

        TriagePolicy.dataFreshness(dataAgeSeconds)?.let(out::add)

        // Without a valid snapshot, omitted fields are unknown rather than zero.
        if (!json.optBoolean("has_data")) return TriagePolicy.sort(out)

        // Shield: the costliest thing to forget.
        val shieldEnd = shield.optLong("end_ms", 0L)
        val shieldLeft = shieldEnd - now
        out += TriagePolicy.shieldTriage(shieldLeft)

        // Daily sign-in.
        val sign = states.optJSONObject("dailySign")
        if (sign != null && sign.length() > 0) {
            if (sign.optBoolean("今日已签")) {
                out += TriageItem("今日已签到", "", Severity.OK)
            } else {
                out += TriageItem(
                    "今日还没签到", "点一下即可补签",
                    Severity.ATTENTION, QuickAction.SIGN.actionLabel, QuickAction.SIGN,
                )
            }
        }

        // Task rewards (daily + weekly + lord).
        val dq = states.optJSONObject("dailyQuest") ?: JSONObject()
        val lord = states.optJSONObject("lordTask") ?: JSONObject()
        val taskN = dq.optJSONArray("可领日常任务")?.length().orZero() +
            dq.optJSONArray("周任务可领奖励")?.length().orZero() +
            lord.optJSONArray("可领奖励")?.length().orZero()
        if (taskN > 0) {
            out += TriageItem(
                "有 $taskN 个任务奖励可领", "日常 / 周 / 领主任务",
                Severity.ATTENTION, QuickAction.CLAIM.actionLabel, QuickAction.CLAIM,
            )
        }

        // Harbor.
        if (dock.optString("family").isNotBlank()) {
            val rewardable = dock.optInt("rewardable", 0)
            if (rewardable > 0) {
                out += TriageItem(
                    "港口有 $rewardable 条船的奖励没领", "在途 ${dock.optInt("trading", 0)} 条",
                    Severity.ATTENTION, QuickAction.DOCK_REWARD.actionLabel, QuickAction.DOCK_REWARD,
                )
            } else {
                out += TriageItem("港口没有待领奖励", "在途 ${dock.optInt("trading", 0)} 条", Severity.OK)
            }
        }

        // Welfare center.
        if (welfare.optBoolean("loaded")) {
            val claimable = welfare.optInt("claimable", 0)
            if (claimable > 0) {
                out += TriageItem(
                    "福利中心有 $claimable 项可领", "每日好礼 / 龙之馈赠",
                    Severity.ATTENTION, QuickAction.WELFARE_CLAIM.actionLabel, QuickAction.WELFARE_CLAIM,
                )
            } else {
                out += TriageItem("福利今天都领完了", "每日好礼 / 龙之馈赠", Severity.OK)
            }
        }

        // Alliance: a pending sign-in is the one daily item the player must do
        // by hand; accepting tasks and donating stay explicit actions.
        if (alliance.optBoolean("loaded")) {
            val summary = alliance.optJSONObject("summary") ?: JSONObject()
            val signIn = summary.optJSONObject("signIn") ?: JSONObject()
            val signDone = signIn.optInt("signInReward_state") == 1
            val researching = summary.optString("researching")
            if (!signDone) {
                out += TriageItem(
                    "联盟签到今日未签", "联盟 · ${researching.ifBlank { "科技" }}",
                    Severity.ATTENTION,
                )
            } else {
                out += TriageItem("联盟签到已完成", "联盟 · ${researching.ifBlank { "科技" }}", Severity.OK)
            }
            if (summary.optBoolean("donateReady")) {
                out += TriageItem(
                    "联盟科技可以捐献", "在研科技 $researching",
                    Severity.ATTENTION, QuickAction.ALLIANCE_DONATE.actionLabel, QuickAction.ALLIANCE_DONATE,
                )
            }
        }

        // Stamina only has meaning when the read itself succeeded. An empty
        // hunt payload otherwise becomes a misleading "0 / 100".
        val staminaSource = if (hunter.optBoolean("running") && hunter.has("stamina")) hunter else hunt
        if (staminaSource.has("stamina")) {
            val stamina = staminaSource.optInt("stamina", 0)
            if (stamina in 1..10) {
                out += TriageItem(
                    "体力只剩 $stamina", "建议等待恢复或用道具", Severity.ATTENTION,
                    operationsFocus = OperationsFocus.HUNT,
                )
            } else if (stamina <= 0) {
                out += TriageItem(
                    "体力已耗尽", "暂时打不了怪", Severity.ATTENTION,
                    operationsFocus = OperationsFocus.HUNT,
                )
            }
        }

        val automation = json.optJSONObject("automation") ?: JSONObject()
        automation.optJSONArray("alerts")?.let { alerts ->
            for (index in 0 until alerts.length()) {
                val alert = alerts.optJSONObject(index) ?: continue
                val label = alert.optString("label").ifBlank { "自动化任务" }
                val failures = alert.optInt("failures").coerceAtLeast(0)
                val reason = alert.optString("reason").ifBlank { "自动化执行失败" }
                out += TriageItem(
                    "${label}需要处理",
                    "$reason${if (failures > 0) " · 已连续失败 $failures 次" else ""}",
                    Severity.RISK,
                    destination = TriageDestination.OPERATIONS,
                )
            }
        }

        return TriagePolicy.sort(out)
    }

    private fun metrics(
        states: JSONObject,
        dock: JSONObject,
        hunter: JSONObject,
        hunt: JSONObject,
        shield: JSONObject,
        welfare: JSONObject,
        json: JSONObject,
    ): List<StatusMetric> {
        if (!json.optBoolean("has_data")) return emptyList()

        val out = mutableListOf<StatusMetric>()
        val now = System.currentTimeMillis()

        val shieldLeft = shield.optLong("end_ms", 0L) - now
        out += StatusMetric(
            "保护罩",
            if (shieldLeft > 0) TriagePolicy.humanDuration(shieldLeft) else "无罩",
            TriagePolicy.shieldSeverity(shieldLeft),
        )

        val staminaSource = if (hunter.optBoolean("running") && hunter.has("stamina")) hunter else hunt
        if (staminaSource.has("stamina")) {
            val stamina = staminaSource.optInt("stamina", 0)
            val staminaMax = staminaSource.optInt("stamina_max", 100).takeIf { it > 0 } ?: 100
            out += StatusMetric(
                "体力", "$stamina / $staminaMax",
                if (stamina <= 10) Severity.ATTENTION else Severity.OK,
            )
        } else {
            out += StatusMetric("体力", "暂未同步", Severity.INFO)
        }

        val gold = if (json.isNull("gold")) null else json.optLong("gold", 0L)
        out += StatusMetric("金币", gold?.let(::groupThousands) ?: "-", Severity.INFO)

        if (dock.optString("family").isNotBlank()) {
            val rewardable = dock.optInt("rewardable", 0)
            out += StatusMetric(
                "港口待领", rewardable.toString(),
                if (rewardable > 0) Severity.ATTENTION else Severity.OK,
            )
        }

        val running = json.optJSONArray("queues")?.let { arr ->
            (0 until arr.length()).count { arr.optJSONObject(it)?.optBoolean("running") == true }
        } ?: 0
        out += StatusMetric("进行队列", running.toString(), Severity.INFO)

        if (hunter.optBoolean("running")) {
            out += StatusMetric("自动打怪", "已打 ${hunter.optInt("kills", 0)}", Severity.OK)
        }

        return out
    }

    private fun operations(
        json: JSONObject,
        hunt: JSONObject,
        hunter: JSONObject,
        shield: JSONObject,
        events: List<ConsoleEvent>,
    ): OperationsSnapshot {
        val shieldLeft = shield.optLong("end_ms") - System.currentTimeMillis()
        val shieldSlots = shield.optJSONArray("slots")?.let { array ->
            buildList {
                for (index in 0 until array.length()) {
                    val slot = array.optJSONObject(index) ?: continue
                    val slotIndex = slot.opt("type")?.toString()?.toIntOrNull() ?: continue
                    val items = slot.optJSONArray("items")?.let { slotItems ->
                        buildList {
                            for (itemIndex in 0 until slotItems.length()) {
                                val item = slotItems.optJSONObject(itemIndex) ?: continue
                                val id = item.opt("id")?.toString().orEmpty()
                                if (id.isBlank()) continue
                                add(
                                    ShieldItem(
                                        id = id,
                                        name = item.optString("name").ifBlank { "保护罩道具" },
                                        duration = item.optString("duration"),
                                        count = item.optInt("num").coerceAtLeast(0),
                                    ),
                                )
                            }
                        }
                    }.orEmpty()
                    add(ShieldSlot(slotIndex, slot.optString("name").ifBlank { "槽位 $slotIndex" }, items))
                }
            }
        }.orEmpty()
        val queues = json.optJSONArray("queues")?.let { array ->
            buildList {
                for (index in 0 until array.length()) {
                    val item = array.optJSONObject(index) ?: continue
                    if (!item.optBoolean("running")) continue
                    add(
                        QueueStatus(
                            uuid = item.optString("uuid"),
                            queueId = item.opt("qid")?.toString().orEmpty(),
                            type = item.optInt("type"),
                            text(item, "type_name").ifBlank { "进行中队列" },
                            text(item, "building_name").ifBlank { "正在进行" },
                            remainingMillis = item.optLong("totalTime").coerceAtLeast(0L),
                        ),
                    )
                }
            }
        }.orEmpty()
        val items = json.optJSONArray("items")?.let { array ->
            buildList {
                for (index in 0 until array.length()) {
                    val item = array.optJSONObject(index) ?: continue
                    val uuid = item.optString("uuid")
                    val count = item.optInt("count")
                    if (uuid.isBlank() || count <= 0) continue
                    add(
                        SpeedupItem(
                            itemId = item.optString("itemId"),
                            uuid = uuid,
                            name = item.optString("name").ifBlank { item.optString("itemId") },
                            label = item.optString("label"),
                            count = count,
                            seconds = item.optLong("seconds").coerceAtLeast(0L),
                            type = item.optInt("type2"),
                        ),
                    )
                }
            }
        }.orEmpty().filter { it.type == UNIVERSAL_SPEEDUP_TYPE }
        val hunting = hunter.optBoolean("running")
        val staminaSource = if (hunting && hunter.has("stamina")) hunter else hunt
        val hasHuntData = staminaSource.has("stamina")
        val stamina = staminaSource.optInt("stamina")
        val staminaMax = staminaSource.optInt("stamina_max", 100).takeIf { it > 0 } ?: 100
        val squads = hunter.optJSONArray("squads")?.let { array ->
            buildList {
                for (index in 0 until array.length()) {
                    val item = array.optJSONObject(index) ?: continue
                    val x = item.opt("x")
                    val y = item.opt("y")
                    val target = if (x != null && y != null && x.toString() != "null" && y.toString() != "null") {
                        "($x, $y)"
                    } else {
                        ""
                    }
                    val troops = item.optJSONArray("troops")?.let { arr ->
                        buildList {
                            for (i in 0 until arr.length()) {
                                val t = arr.optJSONObject(i) ?: continue
                                add(
                                    HuntSquadTroop(
                                        name = text(t, "name").ifBlank { text(t, "army_id") },
                                        num = t.optInt("num"),
                                    ),
                                )
                            }
                        }
                    }.orEmpty()
                    add(
                        HuntSquadStatus(
                            slot = item.optInt("slot", index + 1),
                            name = text(item, "name").ifBlank { "队伍 ${index + 1}" },
                            soldiers = item.optInt("num"),
                            state = text(item, "state").ifBlank { "idle" },
                            kills = item.optInt("kills"),
                            failures = item.optInt("fails"),
                            target = target,
                            elapsedSeconds = item.optInt("elapsed"),
                            note = text(item, "note"),
                            troops = troops,
                        ),
                    )
                }
            }
        }.orEmpty()
        val sky = json.optJSONObject("sky") ?: JSONObject()
        val dock = json.optJSONObject("dock") ?: JSONObject()
        val alliance = alliance(json.optJSONObject("alliance") ?: JSONObject())
        val settings = json.optJSONObject("settings") ?: JSONObject()
        val automation = json.optJSONObject("automation") ?: JSONObject()
        val policy = automation.optJSONObject("policy") ?: JSONObject()
        val rules = automation.optJSONArray("rules")?.let { array ->
            buildList {
                for (index in 0 until array.length()) {
                    val item = array.optJSONObject(index) ?: continue
                    val key = item.optString("key")
                    if (key.isBlank()) continue
                    add(AutomationRule(
                        key = key,
                        label = item.optString("label").ifBlank { key },
                        enabled = item.optBoolean("enabled"),
                        status = item.optString("status").ifBlank { "waiting" },
                        reason = item.optString("reason"),
                        lastAt = item.optLong("last_at"),
                        nextCheckAt = item.optLong("next_check_at"),
                        failures = item.optInt("failures").coerceAtLeast(0),
                    ))
                }
            }
        }.orEmpty()
        val history = automation.optJSONArray("history")?.let { array ->
            buildList {
                for (index in 0 until array.length()) {
                    val item = array.optJSONObject(index) ?: continue
                    add(AutomationHistoryItem(
                        id = item.optString("id").ifBlank { "$index-${item.optLong("at")}" },
                        timestamp = item.optLong("at"),
                        rule = item.optString("rule"),
                        source = item.optString("source").ifBlank { "auto" },
                        status = item.optString("status").ifBlank { "waiting" },
                        summary = item.optString("summary"),
                        reason = item.optString("reason"),
                    ))
                }
            }
        }.orEmpty()
        val alerts = automation.optJSONArray("alerts")?.let { array ->
            buildList {
                for (index in 0 until array.length()) {
                    val item = array.optJSONObject(index) ?: continue
                    val key = item.optString("key")
                    if (key.isBlank()) continue
                    add(AutomationAlert(
                        key = key,
                        label = item.optString("label").ifBlank { key },
                        reason = item.optString("reason"),
                        failures = item.optInt("failures").coerceAtLeast(0),
                        lastAt = item.optLong("last_at"),
                        inBackoff = item.optBoolean("backoff"),
                    ))
                }
            }
        }.orEmpty()
        val automaticEvent = events.firstOrNull { it.kind in AUTOMATION_EVENT_KINDS }
        return OperationsSnapshot(
            shieldActive = shieldLeft > 0,
            shieldStatus = if (shieldLeft > 0) "剩余 ${TriagePolicy.humanDuration(shieldLeft)}" else "当前未开启保护罩",
            automation = AutomationSettings(
                autoSign = settings.optBoolean("autoSign"),
                autoShield = settings.optBoolean("autoShield", shield.optBoolean("autoshield")),
                autoWelfare = settings.optBoolean("autoWelfare"),
                scoreAutoClaim = settings.optBoolean("scoreAutoClaim"),
                dockAutoReward = settings.optBoolean("dockAutoReward"),
                dockAutoSend = settings.optBoolean("dockAutoSend"),
                skyAutoReward = settings.optBoolean("skyAutoReward"),
                skyAutoExplore = settings.optBoolean("skyAutoExplore"),
                allianceDonate = settings.optBoolean("allianceDonate"),
                allianceSignIn = settings.optBoolean("allianceSignIn"),
                assistAuto = settings.optBoolean("assistAuto"),
                assistAutoCostly = settings.optBoolean("assistAutoCostly"),
            ),
            shieldSlots = shieldSlots,
            runningQueues = queues,
            speedupItems = items,
            huntDataAvailable = hasHuntData,
            huntUnavailableReason = hunt.optString("error"),
            hunt = HuntStatus(
                isAvailable = hasHuntData,
                stamina = stamina,
                staminaMax = staminaMax,
                isRunning = hunting,
                kills = hunter.optInt("kills"),
                level = if (hunting) hunter.optInt("level", 1) else settings.optInt("lvLow", hunt.optInt("lv_low", 1)),
                soldiersPerSquad = if (hunting) hunter.optInt("num", 5_000) else settings.optInt("perType", 5_000),
                squadCount = if (hunting) hunter.optInt("squad_max", 4) else settings.optInt("squads", hunt.optInt("auto_count", 4)).coerceIn(1, 8),
                mix = (if (hunting) hunter.optInt("mix", 1) else settings.optInt("huntMix", 1)).coerceIn(1, 4),
                maxKills = if (hunting) hunter.optInt("max_kills") else settings.optInt("huntMax"),
                failures = hunter.optInt("fails"),
                note = text(hunter, "note"),
                waitFor = text(hunter, "wait_for"),
                squads = squads,
                autoStamina = if (hunting) hunter.optBoolean("auto_stamina") else settings.optBoolean("huntAutoStamina"),
                staminaPotions = hunter.optInt("stamina_potions"),
            ),
            sky = SkyStatus(
                stateText = sky.optString("state_text").ifBlank { "尚未读取探索状态" },
                canExplore = sky.optBoolean("can_explore"),
                canClaim = sky.optBoolean("can_reward") || sky.optBoolean("has_reward"),
                reason = sky.optString("explore_reason"),
                remaining = sky.optLong("remain").coerceAtLeast(0L),
                level = sky.optInt("exploreLv").coerceAtLeast(0),
                currentPower = sky.optLong("curPower").coerceAtLeast(0L),
                requiredPower = sky.optLong("needPower").coerceAtLeast(0L),
                lastAutomaticRun = formatTimestamp(sky.opt("last_auto")),
            ),
            dock = DockStatus(
                available = text(dock, "family").isNotBlank() || dock.optBoolean("disabled"),
                disabled = dock.optBoolean("disabled"),
                family = text(dock, "family"),
                rewardable = dock.optInt("rewardable").coerceAtLeast(0),
                trading = dock.optInt("trading").coerceAtLeast(0),
                idle = dock.optInt("idle").coerceAtLeast(0),
                shipLimit = dock.optInt("shipLimit").coerceAtLeast(0),
                cargoClaimable = dock.optBoolean("cargo_claimable"),
                note = text(dock, "note").ifBlank { text(dock, "error") },
                lastReward = lastDockReward(dock.optJSONObject("last_reward")),
                lastAutomaticRun = text(dock, "last_auto"),
            ),
            automationRuntime = AutomationRuntime(
                lastPoll = lastPoll(json),
                autoShieldPersistent = shield.optBoolean("persistent"),
                shieldWatchTicks = shield.optInt("watch_ticks").coerceAtLeast(0),
                shieldWatchIntervalSeconds = shield.optInt("watch_interval").coerceAtLeast(0),
                latestAutomaticEvent = automaticEvent,
            ),
            automationRules = rules,
            automationHistory = history,
            automationAlerts = alerts,
            automationPolicy = AutomationPolicy(
                paused = automation.optBoolean("paused"),
                mode = automation.optString("mode").ifBlank { "execute" },
                maxFailures = policy.optInt("automationMaxFailures", 3).coerceIn(1, 120),
                backoffMinutes = policy.optInt("automationBackoffMinutes", 15).coerceIn(1, 120),
                alertLevel = policy.optString("automationAlertLevel").ifBlank { "failures" },
                huntMinStamina = policy.optInt("huntMinStamina").coerceAtLeast(0),
                skyMinPower = policy.optInt("skyMinPower").coerceAtLeast(0),
                dockMinResourceReserve = policy.optInt("dockMinResourceReserve").coerceAtLeast(0),
            ),
            alliance = alliance,
            assist = assist(json.optJSONObject("assist") ?: JSONObject()),
        )
    }

    /** Parses the web console's `assist` section (the in-game 一键完成 panel). */
    private fun assist(json: JSONObject): QuickAssistStatus? {
        val items = json.optJSONArray("items")?.let { array ->
            buildList {
                for (index in 0 until array.length()) {
                    val item = array.optJSONObject(index) ?: continue
                    add(
                        QuickAssistItem(
                            name = item.optString("name"),
                            groupName = item.optString("groupName"),
                            cost = item.optString("cost"),
                            autoKind = item.optString("autoKind"),
                            state = item.optString("state"),
                        ),
                    )
                }
            }
        }.orEmpty()
        if (items.isEmpty()) return null
        return QuickAssistStatus(
            items = items,
            autoEnabled = json.optBoolean("auto"),
            costly = json.optBoolean("costly"),
            lastDay = json.optString("lastDay"),
        )
    }

    /** Parses the web console's `alliance` section into the native view model. */
    private fun alliance(json: JSONObject): AllianceStatus? {
        if (!json.optBoolean("loaded")) return null
        val summary = json.optJSONObject("summary") ?: JSONObject()
        val researching = json.optJSONObject("researching")
        val task = json.optJSONObject("task") ?: JSONObject()
        val mission = json.optJSONObject("mission") ?: JSONObject()
        val signIn = mission.optJSONObject("signIn") ?: JSONObject()
        val shop = json.optJSONObject("shop") ?: JSONObject()
        val tiers = json.optJSONArray("tiers")?.let { array ->
            buildList {
                for (index in 0 until array.length()) {
                    val item = array.optJSONObject(index) ?: continue
                    val available = if (item.has("available") && !item.isNull("available")) {
                        item.optBoolean("available")
                    } else {
                        null
                    }
                    add(
                        AllianceDonateTier(
                            key = item.optString("key"),
                            name = item.optString("name").ifBlank { item.optString("key") },
                            resource = item.opt("resName")?.toString().orEmpty()
                                .ifBlank { "资源#${item.opt("res")}" },
                            amount = item.opt("num")?.toString().orEmpty(),
                            contribute = item.opt("contribute")?.toString().orEmpty(),
                            progress = item.opt("progress")?.toString().orEmpty(),
                            available = available,
                        ),
                    )
                }
            }
        }.orEmpty()
        return AllianceStatus(
            loaded = true,
            researchingScienceId = researching?.optString("scienceId").orEmpty()
                .ifBlank { summary.optString("researching") },
            researchingLevel = researching?.optInt("level") ?: 0,
            researchingStar = researching?.optInt("star") ?: 0,
            researchingProgress = researching?.let {
                "${it.opt("currentPro")}/${it.opt("needPro")}"
            }.orEmpty(),
            researchingPercent = researching?.optInt("percent") ?: 0,
            researchingFull = researching?.optBoolean("full") ?: false,
            donateReady = json.optBoolean("donateReady"),
            donateReason = json.optString("donateReason"),
            donateTiers = tiers,
            taskAcceptLeft = summary.optInt("taskAcceptLeft"),
            taskPublishLeft = summary.optInt("taskPublishedLeft"),
            publishedTasks = task.optJSONArray("published")?.length() ?: 0,
            pendingTaskCount = summary.optInt("pendingTasks"),
            signInDays = signIn.optInt("signIn_days"),
            signInDone = signIn.optInt("signInReward_state") == 1,
            signInReward = signIn.optString("signIn_reward"),
            alliancePoint = shop.optInt("alliancePoint"),
            autoSignIn = json.optBoolean("autoSignIn"),
            assistAuto = json.optBoolean("assistAuto"),
        )
    }

    private fun mapIndex(index: JSONObject): MapIndexStatus = MapIndexStatus(
        playerCount = index.optInt("count"),
        isScanning = index.optBoolean("scanning"),
        requestsDone = index.optInt("requests_done"),
        requestsTotal = index.optInt("requests_total"),
        percent = index.optDouble("percent").toFloat().coerceIn(0f, 100f),
        isPartial = index.optBoolean("partial"),
        errors = index.optInt("errors"),
        mismatched = index.optInt("mismatched"),
        dropped = index.optInt("dropped"),
    )

    private fun dashboardCards(states: JSONObject, json: JSONObject): List<DashboardCard> {
        val cards = mutableListOf<DashboardCard>()
        val sign = states.optJSONObject("dailySign") ?: JSONObject()
        val quest = states.optJSONObject("dailyQuest") ?: JSONObject()
        val lord = states.optJSONObject("lordTask") ?: JSONObject()
        val story = states.optJSONObject("storyTask") ?: JSONObject()
        val boss = states.optJSONObject("boss") ?: JSONObject()

        if (sign.length() > 0) {
            val signed = sign.optBoolean("今日已签")
            cards += DashboardCard(
                title = "每日签到",
                summary = if (signed) "已完成" else "待签到",
                fields = buildList {
                    add(DashboardField("今日状态", if (signed) "已签到" else "未签到", if (signed) Severity.OK else Severity.ATTENTION))
                    sign.optString("剩余补签次数").takeIf { it.isNotBlank() }?.let { add(DashboardField("剩余补签", it)) }
                    sign.optJSONArray("已签日期")?.let { dates ->
                        val recent = (maxOf(0, dates.length() - 8) until dates.length()).mapNotNull { dates.optString(it).takeIf(String::isNotBlank) }
                        if (recent.isNotEmpty()) add(DashboardField("最近日期", recent.joinToString(" · ")))
                    }
                },
            )
        }

        if (quest.length() > 0) {
            val daily = stringEntries(quest.optJSONArray("可领日常任务"), 4)
            val weekly = stringEntries(quest.optJSONArray("周任务可领奖励"), 4)
            cards += DashboardCard(
                title = "日常与周任务",
                summary = claimSummary(daily.size + weekly.size),
                fields = buildList {
                    quest.optString("周任务积分").takeIf { it.isNotBlank() }?.let { add(DashboardField("周任务积分", it)) }
                    add(DashboardField("可领周奖励", weekly.ifEmpty { listOf("暂无") }.joinToString(" · "), if (weekly.isEmpty()) Severity.OK else Severity.ATTENTION))
                    add(DashboardField("可领日常任务", daily.ifEmpty { listOf("暂无") }.joinToString(" · "), if (daily.isEmpty()) Severity.OK else Severity.ATTENTION))
                    quest.opt("周结束时间")?.let { add(DashboardField("周结束时间", it.toString())) }
                },
            )
        }

        if (lord.length() > 0) {
            val rewards = stringEntries(lord.optJSONArray("可领奖励"), 4)
            val unfinished = stringEntries(lord.optJSONArray("未完成"), 3)
            cards += DashboardCard(
                title = "领主任务",
                summary = claimSummary(rewards.size),
                fields = buildList {
                    lord.optString("当前进度").takeIf { it.isNotBlank() }?.let { add(DashboardField("当前进度", it)) }
                    lord.opt("已领档位数")?.let { add(DashboardField("已领档位", it.toString())) }
                    add(DashboardField("可领奖励", rewards.ifEmpty { listOf("已领完") }.joinToString(" · "), if (rewards.isEmpty()) Severity.OK else Severity.ATTENTION))
                    if (unfinished.isNotEmpty()) add(DashboardField("待完成", unfinished.joinToString(" · ")))
                },
            )
        }

        if (story.length() > 0) {
            val tasks = stringEntries(story.optJSONArray("任务"), 4)
            cards += DashboardCard(
                title = "主线任务",
                summary = story.optString("章节名").ifBlank { story.optString("章节") },
                fields = buildList {
                    story.optString("章节名").ifBlank { story.optString("章节") }.takeIf { it.isNotBlank() }?.let { add(DashboardField("当前章节", it)) }
                    story.opt("任务数")?.let { add(DashboardField("任务数", it.toString())) }
                    if (tasks.isNotEmpty()) add(DashboardField("进行中", tasks.joinToString(" · ")))
                },
            )
        }

        val bosses = boss.optJSONArray("boss")
        if (bosses != null) {
            val entries = (0 until bosses.length()).mapNotNull { index ->
                bosses.optJSONObject(index)?.let { item ->
                    "点 ${item.optString("pointId", "-")} · ${if (item.optBoolean("在位")) "在位" else "不在"} · ${item.optString("num", "0")} 次"
                }
            }
            cards += DashboardCard("联盟 Boss", if (entries.isEmpty()) "暂无 Boss" else "${entries.size} 个", fields = entries.map { DashboardField("状态", it, Severity.INFO) }, emptyMessage = "暂无 Boss")
        }

        val queues = json.optJSONArray("queues")
        if (queues != null) {
            val running = (0 until queues.length()).mapNotNull { queues.optJSONObject(it) }.filter { it.optBoolean("running") }
            cards += DashboardCard(
                title = "进行中的队列",
                summary = if (running.isEmpty()) "当前空闲" else "${running.size} 个进行中",
                fields = running.map { queue ->
                    DashboardField(queue.optString("type_name").ifBlank { "队列" }, queue.optString("building_name").ifBlank { queue.optString("totalTime", "进行中") })
                },
                emptyMessage = "当前没有进行中的队列",
            )
        }

        val overview = states.optJSONObject("overview")?.optJSONArray("队列")
        if (overview != null) {
            val byType = linkedMapOf<String, MutableList<String>>()
            for (index in 0 until overview.length()) {
                val entry = overview.optJSONObject(index) ?: continue
                val type = entry.optString("类型").ifBlank { entry.optString("type", "其他") }
                byType.getOrPut(type) { mutableListOf() } += entry.optString("进度").ifBlank { "进行中" }
            }
            cards += DashboardCard(
                title = "功能概览",
                summary = if (byType.isEmpty()) "暂无进行项" else "${byType.size} 类",
                fields = byType.map { (type, progress) -> DashboardField(type, progress.joinToString(" · ")) },
                emptyMessage = "暂无功能进度",
            )
        }

        return cards
    }

    private fun recentEvents(json: JSONObject): List<ConsoleEvent> {
        val events = json.optJSONArray("events") ?: return emptyList()
        return (0 until events.length()).mapNotNull { index ->
            val event = events.optJSONObject(index) ?: return@mapNotNull null
            val name = event.optString("event").ifBlank { event.optString("type") }
            val data = event.optJSONObject("data") ?: JSONObject()
            val message = data.optString("note")
                .ifBlank { data.optString("error") }
                .ifBlank { name }
            if (message.isBlank()) return@mapNotNull null
            val lower = "$name $message".lowercase()
            ConsoleEvent(
                time = event.optString("time").ifBlank { event.optString("ts") },
                kind = event.optString("kind").ifBlank { name },
                message = message,
                severity = when {
                    "error" in lower || "fail" in lower || "断开" in message -> Severity.RISK
                    "warn" in lower || "等待" in message -> Severity.ATTENTION
                    else -> Severity.INFO
                },
            )
        }.takeLast(12).reversed()
    }

    private fun lastDockReward(reward: JSONObject?): String {
        if (reward == null) return ""
        val count = reward.optInt("count").coerceAtLeast(0)
        val at = formatTimestamp(reward.opt("at"))
        val prefix = if (count > 0) "上次领取 $count 项" else "上次检查无可领奖励"
        return listOf(prefix, at).filter { it.isNotBlank() }.joinToString(" · ")
    }

    private fun formatTimestamp(value: Any?): String {
        val epochSeconds = when (value) {
            is Number -> value.toLong()
            is String -> value.toLongOrNull()
            else -> null
        } ?: return value?.toString().orEmpty().takeUnless { it == "null" }.orEmpty()
        if (epochSeconds <= 0L) return ""
        val ageSeconds = (System.currentTimeMillis() / 1000L - epochSeconds).coerceAtLeast(0L)
        return when {
            ageSeconds < 60 -> "刚刚"
            ageSeconds < 3600 -> "${ageSeconds / 60} 分钟前"
            ageSeconds < 86_400 -> "${ageSeconds / 3600} 小时前"
            else -> "${ageSeconds / 86_400} 天前"
        }
    }

    private fun stringEntries(array: org.json.JSONArray?, limit: Int): List<String> =
        if (array == null) emptyList() else (0 until minOf(array.length(), limit)).mapNotNull { index ->
            when (val item = array.opt(index)) {
                is JSONObject -> item.optString("名称").ifBlank { item.optString("id") }.takeIf { it.isNotBlank() }?.let { name ->
                    item.optString("进度").takeIf { it.isNotBlank() }?.let { "$name $it" } ?: name
                }
                null -> null
                else -> item.toString().takeIf { it.isNotBlank() }
            }
        }

    private fun claimSummary(count: Int): String = if (count > 0) "$count 项可领" else "已领取"

    private fun banner(json: JSONObject): Pair<String?, Boolean> {
        val accountError = text(json, "account_error")
        if (accountError.isNotBlank()) {
            return "设备未连接 · $accountError · 设备连回后点刷新即可恢复" to true
        }
        val source = text(json, "account_source")
        if (source.contains("内置")) {
            val note = text(json, "account_note")
            val prefix = if (note.isNotBlank()) "$note · " else "设备没连上, "
            val dataNote = if (json.optBoolean("has_data")) {
                "数据照常可用，设备连回后点刷新会优先用设备账号"
            } else {
                "正在等待读取游戏数据，设备连回后点刷新会优先用设备账号"
            }
            return "当前使用内置凭据 · $prefix$dataNote" to false
        }
        val error = text(json, "error")
        val hunting = json.optJSONObject("hunter")?.optBoolean("running") == true
        if (error.isNotBlank() && !hunting) {
            return "连接异常 · $error · 点立即刷新重试" to true
        }
        return null to false
    }

    private fun groupThousands(value: Long): String =
        "%,d".format(value)

    private fun text(json: JSONObject, key: String): String =
        json.optString(key).takeUnless { it.isBlank() || it.equals("null", ignoreCase = true) }.orEmpty()

    private fun Int?.orZero(): Int = this ?: 0

    private const val UNIVERSAL_SPEEDUP_TYPE = 1
    private val AUTOMATION_EVENT_KINDS = setOf(
        "dock_auto", "sky_auto", "welfare_auto", "score_auto", "sign",
        "shield_trigger", "shield_result", "shield_watch_error",
    )
}
