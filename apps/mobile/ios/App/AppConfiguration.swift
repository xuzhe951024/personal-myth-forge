import Foundation

enum AppConfiguration {
    static var backendBaseURL: URL {
        if let rawValue = Bundle.main.object(forInfoDictionaryKey: "PMFBackendBaseURL") as? String,
           let url = URL(string: rawValue) {
            return url
        }
        return URL(string: "http://127.0.0.1:8080")!
    }
}
