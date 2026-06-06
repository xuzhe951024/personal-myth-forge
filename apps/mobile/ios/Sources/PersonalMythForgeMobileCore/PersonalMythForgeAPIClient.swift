import Foundation

public struct HTTPResponse: Equatable, Sendable {
    public let statusCode: Int
    public let data: Data

    public init(statusCode: Int, data: Data) {
        self.statusCode = statusCode
        self.data = data
    }
}

public protocol HTTPTransport: Sendable {
    func send(_ request: URLRequest) async throws -> HTTPResponse
}

public struct URLSessionHTTPTransport: HTTPTransport, Sendable {
    public init() {}

    public func send(_ request: URLRequest) async throws -> HTTPResponse {
        let (data, response) = try await URLSession.shared.data(for: request)
        guard let httpResponse = response as? HTTPURLResponse else {
            throw ForgeFlowError.transport("Expected HTTP response.")
        }
        return HTTPResponse(statusCode: httpResponse.statusCode, data: data)
    }
}

public struct CaptureUpload: Equatable, Sendable {
    public let filename: String
    public let contentType: String
    public let data: Data

    public init(filename: String, contentType: String, data: Data) {
        self.filename = filename
        self.contentType = contentType
        self.data = data
    }
}

public enum ForgeFlowError: Error, Equatable, Sendable {
    case invalidBaseURL
    case invalidCaptureID(String)
    case invalidCaptureDraft(String)
    case encodingFailed(String)
    case httpStatus(Int, String)
    case transport(String)
    case decoding(String)
}

public final class PersonalMythForgeAPIClient: ForgeFlowAPI, @unchecked Sendable {
    private static let maxHTTPErrorBodyCharacters = 512
    private static let captureMediaPartSpecs = [
        "image/heic": CaptureMediaPartSpec(prefix: "media", fileExtension: "heic"),
        "image/heif": CaptureMediaPartSpec(prefix: "media", fileExtension: "heif"),
        "image/jpeg": CaptureMediaPartSpec(prefix: "media", fileExtension: "jpg"),
        "image/png": CaptureMediaPartSpec(prefix: "media", fileExtension: "png"),
        "application/octet-stream": CaptureMediaPartSpec(prefix: "scan", fileExtension: "bin"),
        "model/gltf-binary": CaptureMediaPartSpec(prefix: "scan", fileExtension: "glb"),
        "model/vnd.usdz+zip": CaptureMediaPartSpec(prefix: "scan", fileExtension: "usdz"),
    ]

    private let baseURL: URL
    private let transport: any HTTPTransport
    private let boundaryFactory: @Sendable () -> String

    public init(
        baseURL: URL,
        transport: any HTTPTransport = URLSessionHTTPTransport(),
        boundaryFactory: @escaping @Sendable () -> String = { "pmf-\(UUID().uuidString)" }
    ) {
        self.baseURL = baseURL
        self.transport = transport
        self.boundaryFactory = boundaryFactory
    }

    public func uploadObjectCapture(
        metadata: ObjectCaptureMetadata,
        media: [CaptureUpload]
    ) async throws -> ObjectCapture {
        guard !media.isEmpty else {
            throw ForgeFlowError.encodingFailed("At least one capture upload is required.")
        }
        let boundary = boundaryFactory()
        var builder = MultipartFormDataBuilder(boundary: boundary)
        do {
            try builder.appendJSONField(name: "metadata_json", value: metadata)
        } catch {
            throw ForgeFlowError.encodingFailed(String(describing: error))
        }
        for (index, upload) in media.enumerated() {
            let safeMedia = try safeCaptureMediaPart(for: upload, index: index)
            builder.appendFile(
                fieldName: "files",
                filename: safeMedia.filename,
                contentType: safeMedia.contentType,
                data: upload.data
            )
        }

        var request = URLRequest(url: endpoint("/v1/object-captures"))
        request.httpMethod = "POST"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        request.httpBody = builder.build()
        return try await send(request, decoding: ObjectCapture.self)
    }

    public func getObjectCapture(captureId: String) async throws -> ObjectCapture {
        try validateCaptureId(captureId)
        var request = URLRequest(url: endpoint("/v1/object-captures/\(captureId)"))
        request.httpMethod = "GET"
        return try await send(request, decoding: ObjectCapture.self)
    }

    public func createMythSessionFromCapture(
        captureId: String,
        context: ContextCapsule
    ) async throws -> MythSession {
        try validateCaptureId(captureId)
        let body = MythSessionFromCaptureBody(captureId: captureId, contextCapsule: context)
        var request = URLRequest(url: endpoint("/v1/myth-sessions/from-capture"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try encodeJSONBody(body)
        return try await send(request, decoding: MythSession.self)
    }

    public func createDirectMythSession(
        object: ObjectObservation,
        context: ContextCapsule
    ) async throws -> MythSession {
        let body = DirectMythSessionBody(objectObservation: object, contextCapsule: context)
        var request = URLRequest(url: endpoint("/v1/myth-sessions"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try encodeJSONBody(body)
        return try await send(request, decoding: MythSession.self)
    }

    private func endpoint(_ path: String) -> URL {
        let trimmed = path.trimmingCharacters(in: CharacterSet(charactersIn: "/"))
        return baseURL.appendingPathComponent(trimmed)
    }

    private func validateCaptureId(_ captureId: String) throws {
        if !CaptureID.isValid(captureId) {
            throw ForgeFlowError.invalidCaptureID(captureId)
        }
    }

    private func safeCaptureMediaPart(for upload: CaptureUpload, index: Int) throws -> (filename: String, contentType: String) {
        let contentType = upload.contentType
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .lowercased()
        guard let spec = Self.captureMediaPartSpecs[contentType] else {
            throw ForgeFlowError.encodingFailed("Unsupported capture content type.")
        }
        return ("\(spec.prefix)_\(index).\(spec.fileExtension)", contentType)
    }

    private func encodeJSONBody<T: Encodable>(_ body: T) throws -> Data {
        do {
            return try PMFJSON.encoder.encode(body)
        } catch {
            throw ForgeFlowError.encodingFailed(String(describing: error))
        }
    }

    private func send<T: Decodable>(_ request: URLRequest, decoding type: T.Type) async throws -> T {
        let response: HTTPResponse
        do {
            response = try await transport.send(request)
        } catch let error as ForgeFlowError {
            throw error
        } catch {
            throw ForgeFlowError.transport(String(describing: error))
        }

        guard (200...299).contains(response.statusCode) else {
            let body = sanitizedHTTPErrorBody(response.data)
            throw ForgeFlowError.httpStatus(response.statusCode, body)
        }

        do {
            return try PMFJSON.decoder.decode(type, from: response.data)
        } catch {
            throw ForgeFlowError.decoding(String(describing: error))
        }
    }

    private func sanitizedHTTPErrorBody(_ data: Data) -> String {
        var body = String(decoding: data, as: UTF8.self)
        body = replacingMatches(
            in: body,
            pattern: #"(Authorization\s*[:=]\s*Bearer\s+)[^\s,;]+"#
        )
        body = replacingMatches(
            in: body,
            pattern: #"(Bearer\s+)[A-Za-z0-9._~+/\-=]+"#
        )
        body = replacingMatches(
            in: body,
            pattern: #"(raw\s*=\s*)[^\s,;]+"#
        )
        body = replacingMatches(
            in: body,
            pattern: #"((?:api[_-]?key|token|secret)\s*[:=]\s*)[^\s,;]+"#
        )

        if body.count > Self.maxHTTPErrorBodyCharacters {
            return "\(body.prefix(Self.maxHTTPErrorBodyCharacters))...[truncated]"
        }
        return body
    }

    private func replacingMatches(in value: String, pattern: String) -> String {
        guard let regex = try? NSRegularExpression(pattern: pattern, options: [.caseInsensitive]) else {
            return value
        }
        let range = NSRange(value.startIndex..<value.endIndex, in: value)
        return regex.stringByReplacingMatches(
            in: value,
            options: [],
            range: range,
            withTemplate: "$1[redacted]"
        )
    }
}

private struct CaptureMediaPartSpec {
    let prefix: String
    let fileExtension: String
}

private struct MythSessionFromCaptureBody: Encodable {
    let captureId: String
    let contextCapsule: ContextCapsule
}

private struct DirectMythSessionBody: Encodable {
    let objectObservation: ObjectObservation
    let contextCapsule: ContextCapsule
}
