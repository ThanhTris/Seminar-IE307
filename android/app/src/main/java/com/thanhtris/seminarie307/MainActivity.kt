package com.thanhtris.seminarie307

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.compose.runtime.getValue
import com.thanhtris.seminarie307.config.AppContainer
import com.thanhtris.seminarie307.ui.BulletinScreen
import com.thanhtris.seminarie307.ui.BulletinViewModel
import com.thanhtris.seminarie307.ui.theme.SeminarTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        val viewModel = ViewModelProvider(
            this,
            BulletinViewModel.Factory(AppContainer.bulletinUiGateway),
        )[BulletinViewModel::class.java]

        setContent {
            SeminarTheme {
                val state by viewModel.state.collectAsStateWithLifecycle()
                BulletinScreen(
                    viewState = state,
                    onManualSync = viewModel::enqueueManual,
                )
            }
        }
    }
}
