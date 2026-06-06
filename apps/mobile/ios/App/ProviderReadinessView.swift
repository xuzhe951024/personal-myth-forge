import PersonalMythForgeMobileCore
import SwiftUI

struct ProviderReadinessView: View {
    let readiness: ProviderReadinessResponse?
    let errorMessage: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(alignment: .firstTextBaseline) {
                VStack(alignment: .leading, spacing: 2) {
                    Text(statusTitle)
                        .font(.headline)
                    Text(statusDetail)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                Spacer()
            }

            if let readiness {
                VStack(alignment: .leading, spacing: 6) {
                    ForEach(readiness.providers, id: \.kind) { provider in
                        providerRow(provider)
                    }
                }
            }
        }
        .padding(10)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(.thinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
    }

    private var statusTitle: String {
        if errorMessage != nil {
            return "Provider readiness unavailable"
        }
        guard let readiness else {
            return "Checking provider readiness"
        }
        if readiness.overallRealReady {
            return "Real providers ready"
        }
        if readiness.overallDemoReady {
            return "Demo ready, real keys pending"
        }
        return "Provider setup needed"
    }

    private var statusDetail: String {
        if let errorMessage {
            return errorMessage
        }
        guard let readiness else {
            return "Backend preflight will show missing environment names only."
        }
        let missing = readiness.providers.flatMap(\.missingEnv)
        if !missing.isEmpty {
            return "Missing: \(missing.joined(separator: ", "))"
        }
        if readiness.overallRealReady {
            return "External provider configuration is ready for live runs."
        }
        return "Local stubs are active; provider secrets remain backend-only."
    }

    private func providerRow(_ provider: ProviderReadinessItem) -> some View {
        HStack(alignment: .firstTextBaseline, spacing: 8) {
            Circle()
                .fill(statusColor(for: provider))
                .frame(width: 8, height: 8)
            VStack(alignment: .leading, spacing: 1) {
                Text("\(provider.kind) / \(provider.selectedProvider)")
                    .font(.caption.weight(.semibold))
                Text(providerDetail(provider))
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }
            Spacer()
        }
    }

    private func providerDetail(_ provider: ProviderReadinessItem) -> String {
        if !provider.missingEnv.isEmpty {
            return "Missing \(provider.missingEnv.joined(separator: ", "))"
        }
        return provider.status
    }

    private func statusColor(for provider: ProviderReadinessItem) -> Color {
        if provider.isRealProviderReady {
            return .green
        }
        if provider.isDemoReady {
            return .cyan
        }
        return .orange
    }
}
