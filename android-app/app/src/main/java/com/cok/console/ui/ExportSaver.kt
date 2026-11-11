package com.cok.console.ui

import android.content.ContentValues
import android.content.Context
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import android.util.Base64
import android.webkit.JavascriptInterface
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * 导出文件的落盘。
 *
 * 原生界面点「导出已索引玩家 Excel」和 WebView 控制台里的「导出」都走这里,
 * 产物统一在「下载/COK」目录, 两个入口给出同样的提示文案。
 */
fun saveExportToDownloads(context: Context, filename: String, bytes: ByteArray): String =
    runCatching {
        // 文件名带导出时间戳: 同一天反复导出不会被系统改成 "(1) (2)",
        // 也能一眼看出是哪一次扫描的结果。
        val finalName = stampedExportName(filename)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            val values = ContentValues().apply {
                put(MediaStore.Downloads.DISPLAY_NAME, finalName)
                put(
                    MediaStore.Downloads.MIME_TYPE,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
                put(MediaStore.Downloads.RELATIVE_PATH, "Download/COK")
            }
            val uri = context.contentResolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values)
                ?: error("无法创建下载文件")
            context.contentResolver.openOutputStream(uri)?.use { it.write(bytes) }
                ?: error("无法写入下载文件")
            "已导出到 下载/COK/$finalName"
        } else {
            val file = java.io.File(
                context.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS),
                finalName,
            )
            file.parentFile?.mkdirs()
            file.writeBytes(bytes)
            "已导出到 ${file.name}"
        }
    }.getOrElse { "保存导出文件失败：${it.message ?: "未知错误"}" }

/** 给导出文件名加时间戳: cok-players-real.xlsx -> cok-players-real_20261109-1220.xlsx */
private fun stampedExportName(filename: String): String {
    val stamp = SimpleDateFormat("yyyyMMdd-HHmm", Locale.US).format(Date())
    return if (filename.endsWith(".xlsx", ignoreCase = true)) {
        filename.dropLast(5) + "_" + stamp + ".xlsx"
    } else {
        filename
    }
}

/**
 * 给内嵌 WebView 控制台用的 JS 桥。
 *
 * 为什么需要: 网页里的导出是 `fetch -> blob -> <a download>`,
 * **WebView 不会处理 blob 下载** —— 点了没反应, 文件也不落盘,
 * 但页面还会提示"已导出"。所以安卓端要把字节交给原生来存。
 */
class ExportBridge(private val context: Context) {

    @JavascriptInterface
    fun saveExport(filename: String, base64: String): String {
        val safeName = filename.replace(Regex("[^A-Za-z0-9._-]"), "_").ifBlank { "export.xlsx" }
        val bytes = try {
            Base64.decode(base64, Base64.DEFAULT)
        } catch (e: IllegalArgumentException) {
            return "保存导出文件失败：数据解码错误"
        }
        if (bytes.isEmpty()) return "保存导出文件失败：导出内容为空"
        return saveExportToDownloads(context, safeName, bytes)
    }
}
