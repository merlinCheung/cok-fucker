package com.cok.console.ui

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
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.ArrowDropDown
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material3.Text
import androidx.compose.material3.pulltorefresh.PullToRefreshBox
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable

/** Native, triage-first home screen. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    ui: HomeUiState,
    onRefresh: () -> Unit,
    onAction: (QuickAction) -> Unit,
    onOpenOperations: (OperationsFocus?) -> Unit,
    onOpenMore: () -> Unit,
) {
    val snapshot = ui.snapshot
    var pendingAction by rememberSaveable { mutableStateOf<QuickAction?>(null) }
    val requestAction: (QuickAction) -> Unit = { action ->
        if (action.requiresConfirm) pendingAction = action else onAction(action)
    }
    PullToRefreshBox(
        isRefreshing = ui.refreshing,
        onRefresh = onRefresh,
        modifier = Modifier.fillMaxSize(),
    ) {
        if (snapshot == null && ui.loading) {
            HomeSkeleton()
            return@PullToRefreshBox
        }
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(16.dp, 12.dp, 16.dp, 28.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            item { ConnectionHeader(snapshot, ui.refreshing, onRefresh) }

            ui.actionOutcome?.let { outcome ->
                item { HomeActionOutcome(outcome) }
            }

            ui.errorMessage?.let { msg ->
                item { Banner("控制台无响应 · $msg", isError = true) }
            }

            snapshot?.bannerText?.takeIf { snapshot.bannerIsError }?.let { text ->
                item { Banner(text, isError = true) }
            }

            if (snapshot?.gameDataAvailable == true) {
                item { TaskStatsPanel(snapshot.taskStats) }
            }

            val actionable = snapshot?.triage.orEmpty()
                .filter { it.severity == Severity.ATTENTION || it.severity == Severity.RISK }
                .filterNot { it.action != null && it.action in ui.locallyResolvedActions && it.severity != Severity.RISK }
                .sortedWith(
                    compareByDescending<TriageItem> { it.severity.ordinal }
                        .thenByDescending { it.action != null },
                )
            val urgent = actionable.filter { it.severity == Severity.RISK }
            val routine = actionable.filterNot { it.severity == Severity.RISK }

            if (urgent.isNotEmpty()) {
                item { SectionLabel("需要立即处理 ${urgent.size}") }
                items(urgent, key = { "risk-${it.title}-${it.detail}" }) { item ->
                    TriageRow(item, ui.actionInFlight, requestAction, onOpenOperations, onOpenMore)
                }
            }

            item {
                SectionLabel(
                    when {
                        routine.isNotEmpty() -> "今日待办 ${routine.size}"
                        urgent.isNotEmpty() -> "其余状态"
                        else -> "今日待办"
                    },
                )
            }
            if (routine.isEmpty() && urgent.isEmpty()) {
                item { EmptyTriage() }
            } else if (routine.isNotEmpty()) {
                items(routine, key = { "routine-${it.title}-${it.detail}" }) { item ->
                    TriageRow(item, ui.actionInFlight, requestAction, onOpenOperations, onOpenMore)
                }
            } else {
                item { CalmTriage() }
            }

            snapshot?.bannerText?.takeUnless { snapshot.bannerIsError }?.let { text ->
                item { ContextNotice(text) }
            }

            if (snapshot?.gameDataAvailable == true) {
                item { Spacer(Modifier.height(4.dp)) }
                item { StatusSectionHeader { onOpenOperations(null) } }
                item { VitalStatusPanel(snapshot.metrics) }
            }

            if (snapshot?.gameDataAvailable == true && !snapshot.dashboardCards.isEmpty()) {
                item { Spacer(Modifier.height(4.dp)) }
                item { SectionLabel("总览") }
                items(snapshot?.dashboardCards.orEmpty(), key = { it.title }) { card ->
                    DashboardCardRow(card)
                }
            }

        }
    }
    pendingAction?.let { action ->
        QuickActionConfirmation(
            action = action,
            onDismiss = { pendingAction = null },
            onConfirm = { onAction(action); pendingAction = null },
        )
    }
}

private enum class StatsPeriodKind(val title: String) { DAY("今日"), WEEK("本周"), MONTH("本月") }

@Composable
private fun TaskStatsPanel(stats: TaskStats) {
    var selected by rememberSaveable { mutableStateOf(StatsPeriodKind.DAY) }
    var menuOpen by remember { mutableStateOf(false) }
    val period = when (selected) {
        StatsPeriodKind.DAY -> stats.day
        StatsPeriodKind.WEEK -> stats.week
        StatsPeriodKind.MONTH -> stats.month
    }
    Column(
        Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(11.dp))
            .background(CokPalette.surface)
            .border(1.dp, CokPalette.line, RoundedCornerShape(11.dp))
            .padding(14.dp),
    ) {
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text("任务达成明细", color = CokPalette.fg, fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
                Spacer(Modifier.height(3.dp))
                Text("按服务器日期归档，记录已确认完成与成功领取的内容", color = CokPalette.dim, fontSize = 11.sp, lineHeight = 16.sp)
            }
            Spacer(Modifier.width(10.dp))
            Box {
                OutlinedButton(onClick = { menuOpen = true }, shape = RoundedCornerShape(8.dp)) {
                    Text(selected.title, color = CokPalette.accentText, fontSize = 13.sp)
                    Icon(Icons.Filled.ArrowDropDown, contentDescription = "选择统计周期", tint = CokPalette.accentText)
                }
                DropdownMenu(expanded = menuOpen, onDismissRequest = { menuOpen = false }) {
                    StatsPeriodKind.values().forEach { kind ->
                        DropdownMenuItem(
                            text = { Text(kind.title, color = if (kind == selected) CokPalette.accentText else CokPalette.fg) },
                            onClick = { selected = kind; menuOpen = false },
                        )
                    }
                }
            }
        }
        Spacer(Modifier.height(12.dp))
        TaskStatsPeriod(selected.title, period)
    }
}

@Composable
private fun TaskStatsPeriod(title: String, period: TaskStatPeriod) {
    Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
        Text("$title ${period.label}", color = CokPalette.dim2, fontSize = 12.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.weight(1f))
        Text("${period.total} 次", color = if (period.total > 0) CokPalette.ok else CokPalette.dim, fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
    }
    if (period.entries.isEmpty()) {
        Spacer(Modifier.height(6.dp))
        Text("本周期暂无已确认的达成记录", color = CokPalette.dim, fontSize = 12.sp)
        return
    }
    period.entries.forEach { entry ->
        Spacer(Modifier.height(8.dp))
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.Top) {
            Text(entry.label, color = CokPalette.fg, fontSize = 13.sp, modifier = Modifier.weight(1f))
            Text("${entry.count} 次", color = CokPalette.ok, fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
        }
        entry.details.forEach { detail ->
            Spacer(Modifier.height(3.dp))
            Text("${detail.label} · ${detail.count} 次", color = CokPalette.dim, fontSize = 11.sp, lineHeight = 15.sp)
        }
    }
}

@Composable
private fun HomeActionOutcome(outcome: ActionOutcome) {
    val tint = when {
        !outcome.succeeded -> CokPalette.err
        outcome.snapshotVerified -> CokPalette.ok
        else -> CokPalette.warn
    }
    Column(
        Modifier.fillMaxWidth().clip(RoundedCornerShape(10.dp)).background(tint.copy(alpha = .12f))
            .border(1.dp, tint.copy(alpha = .42f), RoundedCornerShape(10.dp)).padding(12.dp),
    ) {
        Text(
            if (outcome.snapshotVerified) "操作已确认 · ${outcome.title}" else "操作结果 · ${outcome.title}",
            color = tint,
            fontSize = 13.sp,
            fontWeight = FontWeight.SemiBold,
        )
        Spacer(Modifier.height(3.dp))
        Text(outcome.detail, color = CokPalette.dim, fontSize = 11.sp, lineHeight = 16.sp)
    }
}

@Composable
private fun ConnectionHeader(snapshot: ConsoleSnapshot?, refreshing: Boolean, onRefresh: () -> Unit) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Column(Modifier.weight(1f)) {
            Text(snapshot?.account ?: "COK 控制台", color = CokPalette.fg, fontSize = 22.sp, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(8.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(
                    Modifier
                        .size(9.dp)
                        .clip(CircleShape)
                        .background(severityColor(snapshot?.connectionSeverity ?: Severity.INFO)),
                )
                Spacer(Modifier.width(8.dp))
                Text(snapshot?.connectionLabel ?: "连接中…", color = CokPalette.dim, fontSize = 13.sp)
                snapshot?.lastPoll?.let { poll ->
                    Text(" · $poll", color = if (snapshot.dataIsStale) CokPalette.warn else CokPalette.dim2, fontSize = 12.sp)
                }
            }
        }
        IconButton(onClick = onRefresh, enabled = !refreshing) {
            Icon(Icons.Filled.Refresh, contentDescription = "刷新状态", tint = CokPalette.accentText)
        }
    }
}

@Composable
private fun Banner(text: String, isError: Boolean) {
    val tint = if (isError) CokPalette.err else CokPalette.warn
    Box(
        Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .background(tint.copy(alpha = 0.12f))
            .border(1.dp, tint.copy(alpha = 0.4f), RoundedCornerShape(10.dp))
            .padding(12.dp),
    ) {
        Text(text, color = CokPalette.fg, fontSize = 12.5.sp, lineHeight = 18.sp)
    }
}

@Composable
private fun ContextNotice(text: String) {
    Row(
        Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(8.dp))
            .background(CokPalette.surface)
            .border(1.dp, CokPalette.line, RoundedCornerShape(8.dp))
            .padding(horizontal = 12.dp, vertical = 10.dp),
        verticalAlignment = Alignment.Top,
    ) {
        Box(
            Modifier
                .padding(top = 5.dp)
                .size(7.dp)
                .clip(CircleShape)
                .background(CokPalette.warn),
        )
        Spacer(Modifier.width(9.dp))
        Text(text, color = CokPalette.dim, fontSize = 12.sp, lineHeight = 17.sp)
    }
}

@Composable
private fun SectionLabel(text: String) {
    Text(
        text.uppercase(),
        color = CokPalette.dim2,
        fontSize = 11.sp,
        fontWeight = FontWeight.Bold,
        letterSpacing = 1.1.sp,
    )
}

@Composable
private fun StatusSectionHeader(onOpenOperations: () -> Unit) {
    Row(
        Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        SectionLabel("关键状态")
        Spacer(Modifier.weight(1f))
        Row(
            Modifier
                .clip(RoundedCornerShape(6.dp))
                .clickable(onClick = onOpenOperations)
                .padding(start = 8.dp, top = 4.dp, bottom = 4.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text("前往操作", color = CokPalette.accentText, fontSize = 12.sp)
            Icon(
                Icons.AutoMirrored.Filled.KeyboardArrowRight,
                contentDescription = "前往操作",
                tint = CokPalette.accentText,
                modifier = Modifier.size(18.dp),
            )
        }
    }
}

@Composable
private fun TriageRow(
    item: TriageItem,
    actionInFlight: QuickAction?,
    onAction: (QuickAction) -> Unit,
    onOpenOperations: (OperationsFocus?) -> Unit,
    onOpenMore: () -> Unit,
) {
    val accent = severityColor(item.severity)
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(11.dp))
            .background(if (item.severity == Severity.RISK) accent.copy(alpha = .10f) else CokPalette.surface)
            .border(
                1.dp,
                if (item.severity == Severity.RISK) accent.copy(alpha = .62f) else CokPalette.line,
                RoundedCornerShape(11.dp),
            )
            .padding(14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            Modifier
                .size(10.dp)
                .clip(CircleShape)
                .background(accent),
        )
        Spacer(Modifier.width(12.dp))
        Column(Modifier.weight(1f)) {
            Text(item.title, color = CokPalette.fg, fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
            if (item.detail.isNotBlank()) {
                Spacer(Modifier.height(2.dp))
                Text(item.detail, color = CokPalette.dim, fontSize = 12.5.sp)
            }
        }
        when {
            item.action != null -> OutlinedButton(
                onClick = { onAction(item.action) },
                enabled = actionInFlight == null,
                shape = RoundedCornerShape(8.dp),
            ) {
                Text(item.actionLabel ?: "处理", color = CokPalette.accentText, fontSize = 12.sp)
            }
            item.severity == Severity.RISK || item.severity == Severity.ATTENTION -> OutlinedButton(
                onClick = {
                    if (item.destination == TriageDestination.MORE) onOpenMore()
                    else onOpenOperations(item.operationsFocus)
                },
                shape = RoundedCornerShape(8.dp),
            ) {
                Text(
                    if (item.destination == TriageDestination.MORE) "连接" else if (item.severity == Severity.RISK) "处理" else "查看",
                    color = CokPalette.accentText,
                    fontSize = 12.sp,
                )
            }
        }
    }
}

@Composable
private fun EmptyTriage() {
    Box(
        Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .background(CokPalette.ok.copy(alpha = 0.08f))
            .border(1.dp, CokPalette.ok.copy(alpha = 0.35f), RoundedCornerShape(10.dp))
            .padding(16.dp),
        contentAlignment = Alignment.Center,
    ) {
        Text("今天没有待处理项", color = CokPalette.ok, fontSize = 13.sp)
    }
}

@Composable
private fun CalmTriage() {
    Box(
        Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .background(CokPalette.surface)
            .border(1.dp, CokPalette.line, RoundedCornerShape(10.dp))
            .padding(14.dp),
    ) {
        Text("没有其他需要处理的日常事项", color = CokPalette.dim, fontSize = 13.sp)
    }
}

@Composable
private fun VitalStatusPanel(metrics: List<StatusMetric>) {
    val leadLabels = setOf("保护罩", "体力")
    val leadMetrics = metrics.filter { it.label in leadLabels }
    val supportingMetrics = metrics.filterNot { it.label in leadLabels }
    Column(
        Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(11.dp))
            .background(CokPalette.surface)
            .border(1.dp, CokPalette.line, RoundedCornerShape(11.dp))
            .padding(13.dp),
    ) {
        if (leadMetrics.isNotEmpty()) {
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp), modifier = Modifier.fillMaxWidth()) {
                leadMetrics.forEach { metric ->
                    LeadMetric(metric, Modifier.weight(1f))
                }
                if (leadMetrics.size == 1) Spacer(Modifier.weight(1f))
            }
        }
        if (supportingMetrics.isNotEmpty()) {
            if (leadMetrics.isNotEmpty()) {
                Spacer(Modifier.height(12.dp))
                HorizontalDivider(color = CokPalette.line)
                Spacer(Modifier.height(4.dp))
            }
            supportingMetrics.forEach { metric ->
                CompactMetric(metric)
            }
        }
    }
}

@Composable
private fun LeadMetric(metric: StatusMetric, modifier: Modifier = Modifier) {
    Column(modifier) {
        Text(metric.label, color = CokPalette.dim2, fontSize = 11.sp)
        Spacer(Modifier.height(5.dp))
        Text(metric.value, color = severityColor(metric.severity), fontSize = 20.sp, fontWeight = FontWeight.Bold, maxLines = 1)
    }
}

@Composable
private fun CompactMetric(metric: StatusMetric) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(metric.label, color = CokPalette.dim, fontSize = 13.sp, modifier = Modifier.weight(1f))
        Text(metric.value, color = severityColor(metric.severity), fontSize = 14.sp, fontWeight = FontWeight.SemiBold, maxLines = 1)
    }
}

@Composable
private fun DashboardCardRow(card: DashboardCard) {
    var expanded by rememberSaveable(card.title) { mutableStateOf(false) }
    Column(
        Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(11.dp))
            .background(CokPalette.surface)
            .border(1.dp, CokPalette.line, RoundedCornerShape(11.dp))
            .clickable { expanded = !expanded }
            .padding(14.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(card.title, Modifier.weight(1f), color = CokPalette.fg, fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
            Text(
                card.summary,
                color = if (card.summary.contains("可领") || card.summary.contains("待")) CokPalette.warn else CokPalette.dim,
                fontSize = 12.sp,
            )
        }
        if (expanded) {
            Spacer(Modifier.height(10.dp))
            if (card.fields.isEmpty()) {
                Text(card.emptyMessage ?: "暂无详细数据", color = CokPalette.dim, fontSize = 12.sp)
            } else {
                card.fields.forEach { field ->
                    Row(Modifier.fillMaxWidth().padding(vertical = 4.dp), verticalAlignment = Alignment.Top) {
                        Text(field.label, Modifier.weight(.38f), color = CokPalette.dim2, fontSize = 12.sp)
                        Text(field.value, Modifier.weight(.62f), color = severityColor(field.severity), fontSize = 12.sp)
                    }
                }
            }
        }
    }
}

@Composable
private fun HomeSkeleton() {
    Column(
        Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        repeat(6) {
            Box(
                Modifier
                    .fillMaxWidth()
                    .height(if (it == 0) 54.dp else 68.dp)
                    .clip(RoundedCornerShape(11.dp))
                    .background(CokPalette.surface),
            )
        }
    }
}

internal fun severityColor(severity: Severity): Color = when (severity) {
    Severity.OK -> CokPalette.ok
    Severity.INFO -> CokPalette.accent
    Severity.ATTENTION -> CokPalette.warn
    Severity.RISK -> CokPalette.err
}
