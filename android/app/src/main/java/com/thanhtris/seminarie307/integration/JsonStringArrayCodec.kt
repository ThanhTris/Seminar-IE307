package com.thanhtris.seminarie307.integration

/** Minimal JSON string-array encoder that does not depend on Android's JVM test stubs. */
object JsonStringArrayCodec {
    fun encode(values: List<String>): String = values.joinToString(
        separator = ",",
        prefix = "[",
        postfix = "]",
        transform = ::quoteString,
    )

    fun objectOf(fields: List<Pair<String, String>>): String = fields.joinToString(
        separator = ",",
        prefix = "{",
        postfix = "}",
    ) { (key, rawJsonValue) -> "${quoteString(key)}:$rawJsonValue" }

    /** Decode JSON arrays written by previous app versions without Android's org.json stubs. */
    fun decode(json: String): List<String> {
        var index = 0
        fun skipWhitespace() {
            while (index < json.length && json[index].isWhitespace()) index++
        }

        skipWhitespace()
        require(index < json.length && json[index++] == '[') { "Expected JSON array" }
        skipWhitespace()
        if (index < json.length && json[index] == ']') {
            index++
            skipWhitespace()
            require(index == json.length) { "Unexpected data after JSON array" }
            return emptyList()
        }

        val values = mutableListOf<String>()
        while (index < json.length) {
            skipWhitespace()
            require(index < json.length && json[index++] == '"') { "Expected JSON string" }
            val value = StringBuilder()
            var closed = false
            while (index < json.length && !closed) {
                val char = json[index++]
                when (char) {
                    '"' -> closed = true
                    '\\' -> {
                        require(index < json.length) { "Incomplete JSON escape" }
                        when (val escaped = json[index++]) {
                            '"', '\\', '/' -> value.append(escaped)
                            'b' -> value.append('\b')
                            'f' -> value.append('\u000C')
                            'n' -> value.append('\n')
                            'r' -> value.append('\r')
                            't' -> value.append('\t')
                            'u' -> {
                                require(index + 4 <= json.length) { "Incomplete unicode escape" }
                                val code = json.substring(index, index + 4).toIntOrNull(16)
                                    ?: error("Invalid unicode escape")
                                value.append(code.toChar())
                                index += 4
                            }
                            else -> error("Invalid JSON escape")
                        }
                    }
                    else -> {
                        require(char.code >= 0x20) { "Unescaped control character" }
                        value.append(char)
                    }
                }
            }
            require(closed) { "Unterminated JSON string" }
            values += value.toString()
            skipWhitespace()
            require(index < json.length) { "Unterminated JSON array" }
            when (json[index++]) {
                ']' -> {
                    skipWhitespace()
                    require(index == json.length) { "Unexpected data after JSON array" }
                    return values
                }
                ',' -> Unit
                else -> error("Expected comma or closing bracket")
            }
        }
        error("Unterminated JSON array")
    }

    fun quoteString(value: String): String = buildString {
        append('"')
        value.forEach { char ->
            when (char) {
                '"' -> append("\\\"")
                '\\' -> append("\\\\")
                '\b' -> append("\\b")
                '\u000C' -> append("\\f")
                '\n' -> append("\\n")
                '\r' -> append("\\r")
                '\t' -> append("\\t")
                else -> if (char.code < 0x20) {
                    append("\\u")
                    append(char.code.toString(16).padStart(4, '0'))
                } else {
                    append(char)
                }
            }
        }
        append('"')
    }
}
