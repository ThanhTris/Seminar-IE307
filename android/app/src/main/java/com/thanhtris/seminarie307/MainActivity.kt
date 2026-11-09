package com.thanhtris.seminarie307

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
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
    private val requestLocalNetwork = registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        if (!granted) {
            Toast.makeText(this, R.string.local_network_permission_required, Toast.LENGTH_LONG).show()
        }
    }

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

        if (Build.VERSION.SDK_INT >= 37 &&
            checkSelfPermission(Manifest.permission.ACCESS_LOCAL_NETWORK) != PackageManager.PERMISSION_GRANTED
        ) {
            requestLocalNetwork.launch(Manifest.permission.ACCESS_LOCAL_NETWORK)
        }
    }
}
