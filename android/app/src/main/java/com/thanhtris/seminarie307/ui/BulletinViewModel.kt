package com.thanhtris.seminarie307.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.thanhtris.seminarie307.integration.BulletinUiGateway
import com.thanhtris.seminarie307.integration.BulletinUiState
import com.thanhtris.seminarie307.integration.ManualEnqueueResult
import com.thanhtris.seminarie307.integration.ManualSyncContext
import com.thanhtris.seminarie307.integration.SyncMode
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class BulletinViewState(
    val data: BulletinUiState = BulletinUiState(),
    val manualFeedback: String? = null,
    val isEnqueueing: Boolean = false,
)

class BulletinViewModel(private val gateway: BulletinUiGateway) : ViewModel() {
    private val mutableState = MutableStateFlow(BulletinViewState())
    val state = mutableState.asStateFlow()

    init {
        viewModelScope.launch {
            gateway.state.collect { observed ->
                mutableState.update { current -> current.copy(data = observed) }
            }
        }
    }

    fun enqueueManual(context: ManualSyncContext) {
        val observed = mutableState.value.data
        if (!observed.canEnqueueManual || observed.manualContextOrNull() != context || mutableState.value.isEnqueueing) {
            mutableState.update {
                it.copy(manualFeedback = "Đồng bộ chưa khả dụng cho run hiện tại.")
            }
            return
        }

        viewModelScope.launch {
            mutableState.update { it.copy(isEnqueueing = true, manualFeedback = null) }
            val result = try {
                gateway.enqueueManual(context)
            } catch (cancelled: CancellationException) {
                throw cancelled
            } catch (failure: Exception) {
                ManualEnqueueResult.Rejected(failure.message ?: "Không thể xếp lịch đồng bộ.")
            }
            mutableState.update {
                it.copy(
                    isEnqueueing = false,
                    manualFeedback = when (result) {
                        ManualEnqueueResult.Accepted -> "Đã xếp lịch; chưa xác nhận đã đồng bộ."
                        is ManualEnqueueResult.Rejected -> "Không xếp được: ${result.reason}"
                    },
                )
            }
        }
    }

    fun configureMode(mode: SyncMode, runId: String, deviceAlias: String) {
        val normalizedRunId = runId.trim()
        val normalizedDeviceAlias = deviceAlias.trim()
        if (normalizedRunId.isBlank() || normalizedDeviceAlias.isBlank()) {
            mutableState.update { it.copy(manualFeedback = "Nhập run ID và device alias trước khi cấu hình mode.") }
            return
        }
        viewModelScope.launch {
            mutableState.update { it.copy(manualFeedback = null) }
            try {
                gateway.configureMode(mode, normalizedRunId, normalizedDeviceAlias)
                mutableState.update {
                    it.copy(manualFeedback = "Đã chuyển sang mode ${mode.name}; kiểm tra timeline trước khi đo.")
                }
            } catch (cancelled: CancellationException) {
                throw cancelled
            } catch (failure: Exception) {
                mutableState.update {
                    it.copy(manualFeedback = "Không đổi được mode: ${failure.message ?: "lỗi không xác định"}")
                }
            }
        }
    }

    class Factory(private val gateway: BulletinUiGateway) : ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            require(modelClass.isAssignableFrom(BulletinViewModel::class.java))
            return BulletinViewModel(gateway) as T
        }
    }
}
