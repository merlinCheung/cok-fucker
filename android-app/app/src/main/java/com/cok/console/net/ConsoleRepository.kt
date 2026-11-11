package com.cok.console.net

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.BufferedReader
import java.net.HttpURLConnection
import java.net.URL

/**
 * Thin client over the same loopback API the web console uses.
 *
 * It intentionally keeps no business logic: the Python server still owns account
 * locking, yielding, formations, and risk handling. This only transports JSON.
 */
class ConsoleRepository(
    private val baseUrl: String,
    private val token: String,
) {
    suspend fun fetchState(): Result<JSONObject> = request("GET", "/api/state", null)

    suspend fun fetchScanStatus(): Result<JSONObject> = request("GET", "/api/scan/status", null)

    suspend fun fetchScanHistory(): Result<JSONObject> = request("GET", "/api/scan/history", null)

    suspend fun startScan(step: Int, resume: Boolean): Result<JSONObject> =
        request("POST", "/api/scan/start", JSONObject().put("step", step).put("resume", resume))

    suspend fun stopScan(): Result<JSONObject> = request("POST", "/api/scan/stop", JSONObject())

    suspend fun exportPlayers(playersOnly: Boolean): Result<ByteArray> = withContext(Dispatchers.IO) {
        runCatching {
            val suffix = if (playersOnly) "?players=1" else ""
            val conn = (URL("$baseUrl/api/export$suffix").openConnection() as HttpURLConnection).apply {
                requestMethod = "GET"
                connectTimeout = 8000
                readTimeout = 30000
                setRequestProperty("X-Cok-Token", token)
            }
            val code = conn.responseCode
            if (code !in 200..299) {
                val error = conn.errorStream?.bufferedReader()?.use(BufferedReader::readText).orEmpty()
                conn.disconnect()
                val message = runCatching { JSONObject(error).optString("error") }.getOrDefault("")
                throw IllegalStateException(message.ifBlank { "HTTP $code" })
            }
            val bytes = conn.inputStream.use { it.readBytes() }
            conn.disconnect()
            bytes
        }
    }

    suspend fun action(body: JSONObject): Result<JSONObject> {
        // The embedded server may need to finish a game-server handshake before
        // replying. A single 20-second limit made a successful reconnect look
        // like a client-side timeout on slower mobile networks.
        val readTimeoutMs = when (body.optString("action")) {
            "refresh-now" -> 240_000
            "reconnect" -> 75_000
            else -> 45_000
        }
        return request("POST", "/api/action", body, readTimeoutMs)
    }

    private suspend fun request(
        method: String,
        path: String,
        body: JSONObject?,
        readTimeoutMs: Int = 20_000,
    ): Result<JSONObject> = withContext(Dispatchers.IO) {
        runCatching {
            val conn = (URL("$baseUrl$path").openConnection() as HttpURLConnection).apply {
                requestMethod = method
                connectTimeout = 8000
                readTimeout = readTimeoutMs
                setRequestProperty("X-Cok-Token", token)
                setRequestProperty("Accept", "application/json")
                if (body != null) {
                    doOutput = true
                    setRequestProperty("Content-Type", "application/json; charset=utf-8")
                    outputStream.use { it.write(body.toString().toByteArray(Charsets.UTF_8)) }
                }
            }
            val code = conn.responseCode
            val stream = if (code in 200..299) conn.inputStream else conn.errorStream
            val text = stream?.bufferedReader()?.use(BufferedReader::readText).orEmpty()
            conn.disconnect()
            if (text.isBlank()) JSONObject() else JSONObject(text)
        }
    }
}
