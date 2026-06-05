import Foundation

public struct MultipartFormDataBuilder {
    private static let headerParameterScalars = CharacterSet(
        charactersIn: "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
    )
    private static let filenameScalars = CharacterSet(
        charactersIn: "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
    )
    private static let contentTypeScalars = CharacterSet(
        charactersIn: "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.+-/"
    )

    public let boundary: String
    private var chunks: [Data] = []

    public init(boundary: String) {
        self.boundary = boundary
    }

    public mutating func appendJSONField<T: Encodable>(name: String, value: T) throws {
        let json = try PMFJSON.encoder.encode(value)
        let safeName = safeHeaderParameter(name, fallback: "field")
        appendLine("--\(boundary)")
        appendLine("Content-Disposition: form-data; name=\"\(safeName)\"")
        appendLine("Content-Type: application/json")
        appendLine("")
        chunks.append(json)
        appendLine("")
    }

    public mutating func appendFile(
        fieldName: String,
        filename: String,
        contentType: String,
        data: Data
    ) {
        let safeFieldName = safeHeaderParameter(fieldName, fallback: "file")
        let safeFilename = safeFilename(filename)
        let safeContentType = safeContentType(contentType)
        appendLine("--\(boundary)")
        appendLine("Content-Disposition: form-data; name=\"\(safeFieldName)\"; filename=\"\(safeFilename)\"")
        appendLine("Content-Type: \(safeContentType)")
        appendLine("")
        chunks.append(data)
        appendLine("")
    }

    public func build() -> Data {
        var body = Data()
        for chunk in chunks {
            body.append(chunk)
        }
        body.append(Data("--\(boundary)--\r\n".utf8))
        return body
    }

    private mutating func appendLine(_ value: String) {
        chunks.append(Data("\(value)\r\n".utf8))
    }

    private func safeHeaderParameter(_ value: String, fallback: String) -> String {
        let filtered = filteredScalars(firstHeaderLine(value), allowed: Self.headerParameterScalars)
        return filtered.isEmpty ? fallback : filtered
    }

    private func safeFilename(_ value: String) -> String {
        let pathNormalized = value.replacingOccurrences(of: "\\", with: "/")
        let leaf = pathNormalized.split(separator: "/", omittingEmptySubsequences: true)
            .last
            .map(String.init) ?? value
        let filtered = filteredScalars(firstHeaderLine(leaf), allowed: Self.filenameScalars)
        if filtered.isEmpty || filtered == "." || filtered == ".." {
            return "upload.bin"
        }
        return filtered
    }

    private func safeContentType(_ value: String) -> String {
        let trimmed = value.trimmingCharacters(in: .whitespacesAndNewlines)
        let filtered = filteredScalars(trimmed, allowed: Self.contentTypeScalars)
        guard !trimmed.isEmpty, filtered == trimmed, trimmed.contains("/") else {
            return "application/octet-stream"
        }
        return trimmed.lowercased()
    }

    private func firstHeaderLine(_ value: String) -> String {
        if let newline = value.rangeOfCharacter(from: .newlines) {
            return String(value[..<newline.lowerBound])
        }
        return value
    }

    private func filteredScalars(_ value: String, allowed: CharacterSet) -> String {
        var scalars = String.UnicodeScalarView()
        for scalar in value.unicodeScalars where allowed.contains(scalar) {
            scalars.append(scalar)
        }
        return String(scalars)
    }
}
