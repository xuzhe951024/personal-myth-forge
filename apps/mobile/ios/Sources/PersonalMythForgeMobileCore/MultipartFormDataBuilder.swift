import Foundation

public struct MultipartFormDataBuilder {
    public let boundary: String
    private var chunks: [Data] = []

    public init(boundary: String) {
        self.boundary = boundary
    }

    public mutating func appendJSONField<T: Encodable>(name: String, value: T) throws {
        let json = try PMFJSON.encoder.encode(value)
        appendLine("--\(boundary)")
        appendLine("Content-Disposition: form-data; name=\"\(name)\"")
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
        appendLine("--\(boundary)")
        appendLine("Content-Disposition: form-data; name=\"\(fieldName)\"; filename=\"\(filename)\"")
        appendLine("Content-Type: \(contentType)")
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
}
