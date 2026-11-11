package com.cok.console.ui

import android.annotation.SuppressLint
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.viewinterop.AndroidView

/**
 * Full desktop console embedded as a zero-loss fallback.
 *
 * Everything the native screens do not cover yet (scan config, player locate,
 * formations, channel login) stays reachable here with the exact same behavior.
 */
@SuppressLint("SetJavaScriptEnabled")
@Composable
fun ConsoleWebScreen(fullUrl: String) {
    val embeddedUrl = remember(fullUrl) { "$fullUrl&embed=1" }
    AndroidView(
        modifier = Modifier.fillMaxSize(),
        factory = { context ->
            WebView(context).apply {
                settings.javaScriptEnabled = true
                settings.domStorageEnabled = true
                settings.allowFileAccess = false
                settings.allowContentAccess = false
                // 网页里的「导出」是 blob 下载, WebView 不会落盘 —— 交给原生存。
                addJavascriptInterface(ExportBridge(context), "CokAndroid")
                webViewClient = object : WebViewClient() {
                    override fun shouldOverrideUrlLoading(
                        view: WebView,
                        request: WebResourceRequest,
                    ): Boolean {
                        val host = request.url.host
                        return host == null || host != "127.0.0.1"
                    }
                }
                loadUrl(embeddedUrl)
            }
        },
        update = { webView ->
            val current = webView.url
            if (current == null || !current.startsWith(embeddedUrl.substringBefore("/?"))) {
                webView.loadUrl(embeddedUrl)
            }
        },
    )
}
