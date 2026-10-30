package com.thanhtris.seminarie307.ui

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Tab
import androidx.compose.material3.PrimaryTabRow
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardCapitalization
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.thanhtris.seminarie307.integration.BulletinItem
import com.thanhtris.seminarie307.integration.BulletinUiState
import com.thanhtris.seminarie307.integration.CorrelationUi
import com.thanhtris.seminarie307.integration.ManualSyncContext
import com.thanhtris.seminarie307.integration.SyncMode
import com.thanhtris.seminarie307.integration.SyncSource
import com.thanhtris.seminarie307.integration.TimelineEvent

private enum class BulletinTab(val label: String) {
    BULLETIN("Bản tin"),
    TIMELINE("Timeline"),
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BulletinScreen(
    viewState: BulletinViewState,
    onManualSync: (ManualSyncContext) -> Unit,
    modifier: Modifier = Modifier,
) {
    var selectedTabName by rememberSaveable { mutableStateOf(BulletinTab.BULLETIN.name) }
    var runFilter by rememberSaveable { mutableStateOf("") }
    val selectedTab = BulletinTab.valueOf(selectedTabName)

    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text("Seminar IE307")
                        Text(
                            text = "Đồng bộ bảng tin Android",
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                },
            )
        },
    ) { contentPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(contentPadding),
        ) {
            StatusSummary(viewState.data)
            PrimaryTabRow(selectedTabIndex = selectedTab.ordinal) {
                BulletinTab.entries.forEach { tab ->
                    Tab(
                        selected = selectedTab == tab,
                        onClick = { selectedTabName = tab.name },
                        text = { Text(tab.label) },
                    )
                }
            }

            when (selectedTab) {
                BulletinTab.BULLETIN -> BulletinContent(
                    data = viewState.data,
                    viewState = viewState,
                    onManualSync = onManualSync,
                    modifier = Modifier.weight(1f),
                )

                BulletinTab.TIMELINE -> TimelineContent(
                    events = viewState.data.timeline,
                    filter = runFilter,
                    onFilterChange = { runFilter = it },
                    modifier = Modifier.weight(1f),
                )
            }
        }
    }
}

@Composable
private fun StatusSummary(state: BulletinUiState) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 10.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceContainer),
    ) {
        Column(
            modifier = Modifier.padding(horizontal = 16.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            StatusLine("Version cache", state.cachedVersion?.let { "v$it" } ?: "—")
            StatusLine("Mode", state.mode?.label() ?: "Chưa cấu hình")
            StatusLine("Lần sync gần nhất", state.lastSyncAtUtc ?: "Chưa đồng bộ")
        }
    }
}

@Composable
private fun StatusLine(label: String, value: String) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(label, style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(
            value,
            modifier = Modifier.padding(start = 12.dp),
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Medium,
            maxLines = 2,
            overflow = TextOverflow.Ellipsis,
        )
    }
}

@Composable
private fun BulletinContent(
    data: BulletinUiState,
    viewState: BulletinViewState,
    onManualSync: (ManualSyncContext) -> Unit,
    modifier: Modifier = Modifier,
) {
    LazyColumn(
        modifier = modifier.fillMaxWidth(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        if (data.snapshot.isEmpty()) {
            item {
                EmptyCard(
                    title = "Chưa có bản tin trong cache",
                    description = "Bản tin sẽ xuất hiện sau khi sync core lưu snapshot vào máy.",
                )
            }
        } else {
            items(data.snapshot, key = BulletinItem::id) { item ->
                BulletinCard(item)
            }
        }

        item {
            val context = data.manualContextOrNull()
            val canEnqueue = data.canEnqueueManual && !viewState.isEnqueueing
            Button(
                onClick = { context?.let(onManualSync) },
                enabled = canEnqueue,
                modifier = Modifier.fillMaxWidth(),
            ) {
                if (viewState.isEnqueueing) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(18.dp),
                        strokeWidth = 2.dp,
                        color = MaterialTheme.colorScheme.onPrimary,
                    )
                    Spacer(Modifier.size(8.dp))
                }
                Text(if (viewState.isEnqueueing) "Đang xếp lịch…" else "Đồng bộ thủ công")
            }
        }

        if (!data.canEnqueueManual) {
            item {
                Text(
                    text = "Đồng bộ chưa khả dụng: chưa có gateway hoặc run đang hoạt động.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }

        viewState.manualFeedback?.let { message ->
            item {
                Text(
                    text = message,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.primary,
                )
            }
        }
    }
}

@Composable
private fun EmptyCard(title: String, description: String) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
    ) {
        Column(Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
            Text(description, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}

@Composable
private fun BulletinCard(item: BulletinItem) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(item.title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
            Text(item.body, style = MaterialTheme.typography.bodyLarge)
            Text("Version v${item.version}", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.primary)
        }
    }
}

@Composable
private fun TimelineContent(
    events: List<TimelineEvent>,
    filter: String,
    onFilterChange: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    val filteredEvents = filterTimeline(events, filter)
    Column(modifier = modifier.fillMaxWidth()) {
        OutlinedTextField(
            value = filter,
            onValueChange = onFilterChange,
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 10.dp),
            label = { Text("Lọc theo run_id") },
            supportingText = { Text("So khớp chính xác; để trống để xem mọi run.") },
            singleLine = true,
            keyboardOptions = KeyboardOptions(capitalization = KeyboardCapitalization.None),
        )

        if (filteredEvents.isEmpty()) {
            EmptyCard(
                title = if (filter.isBlank()) "Chưa có sự kiện" else "Không có sự kiện cho run này",
                description = if (filter.isBlank()) {
                    "Timeline sẽ hiển thị các trigger và kết quả được ghi local."
                } else {
                    "Kiểm tra run_id hoặc xóa bộ lọc để xem toàn bộ timeline."
                },
            )
        } else {
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(start = 16.dp, end = 16.dp, bottom = 20.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                items(filteredEvents, key = TimelineEvent::eventId) { event ->
                    TimelineCard(event)
                }
            }
        }
    }
}

@Composable
private fun TimelineCard(event: TimelineEvent) {
    var expanded by rememberSaveable(event.eventId) { mutableStateOf(false) }
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { expanded = !expanded },
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text = event.source?.label() ?: "Nguồn chưa rõ",
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.primary,
                )
                Text(event.eventType, style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.SemiBold)
            }
            Text(event.occurredAtUtc, style = MaterialTheme.typography.bodySmall)
            Text("run_id: ${event.runId ?: "—"}", style = MaterialTheme.typography.bodyMedium)
            val details = listOfNotNull(
                event.version?.let { "v$it" },
                event.outcome,
                event.reason,
            ).joinToString(" · ")
            if (details.isNotEmpty()) Text(details, style = MaterialTheme.typography.bodySmall)

            if (expanded) {
                HorizontalDivider(Modifier.padding(vertical = 4.dp))
                CorrelationDetails(event.correlation)
            } else if (event.correlation.hasAnyId()) {
                Text(
                    "Chi tiết correlation",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.primary,
                )
            }
        }
    }
}

@Composable
private fun CorrelationDetails(correlation: CorrelationUi?) {
    if (correlation == null || !correlation.hasAnyId()) {
        Text("Không có correlation ID.", style = MaterialTheme.typography.bodySmall)
        return
    }
    Column(verticalArrangement = Arrangement.spacedBy(3.dp)) {
        correlation.requestId?.let { Text("request_id: $it", style = MaterialTheme.typography.bodySmall) }
        correlation.workId?.let { Text("work_id: $it", style = MaterialTheme.typography.bodySmall) }
        correlation.messageId?.let { Text("message_id: $it", style = MaterialTheme.typography.bodySmall) }
    }
}

private fun CorrelationUi?.hasAnyId(): Boolean =
    this != null && listOf(requestId, workId, messageId).any { !it.isNullOrBlank() }

private fun SyncMode.label(): String = when (this) {
    SyncMode.PERIODIC -> "PERIODIC"
    SyncMode.PUSH -> "PUSH"
    SyncMode.HYBRID -> "HYBRID"
}

private fun SyncSource.label(): String = when (this) {
    SyncSource.MANUAL -> "MANUAL"
    SyncSource.PERIODIC -> "PERIODIC"
    SyncSource.PUSH -> "PUSH"
}
