import PersonalMythForgeMobileCore
import SwiftUI

struct DevicePreflightView: View {
    let summary: DevicePreflightSummary

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .firstTextBaseline) {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Device Preflight")
                        .font(.headline)
                    Text(summary.title)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .lineLimit(2)
                }
                Spacer(minLength: 8)
                Text(statusBadge)
                    .font(.caption2.weight(.bold))
                    .foregroundStyle(statusColor)
            }

            Text(summary.backendBaseURL)
                .font(.caption2)
                .foregroundStyle(.secondary)
                .lineLimit(1)
                .truncationMode(.middle)
                .textSelection(.enabled)

            VStack(alignment: .leading, spacing: 6) {
                ForEach(summary.items, id: \.id) { item in
                    itemRow(item)
                }
            }

            if !summary.notes.isEmpty {
                Text(summary.notes.joined(separator: " "))
                    .font(.caption2)
                    .foregroundStyle(.secondary)
                    .lineLimit(3)
            }
        }
        .padding(10)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(.thinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
    }

    private var statusBadge: String {
        switch summary.overallStatus {
        case .blocked:
            return "BLOCKED"
        case .waiting:
            return "WAITING"
        case .ready:
            return "READY"
        }
    }

    private var statusColor: Color {
        color(for: summary.overallStatus)
    }

    private func itemRow(_ item: DevicePreflightItem) -> some View {
        HStack(alignment: .firstTextBaseline, spacing: 8) {
            Circle()
                .fill(color(for: item.status))
                .frame(width: 8, height: 8)
            Text(item.label)
                .font(.caption.weight(.semibold))
                .frame(width: 78, alignment: .leading)
            Text(item.detail)
                .font(.caption2)
                .foregroundStyle(.secondary)
                .lineLimit(2)
            Spacer(minLength: 0)
        }
    }

    private func color(for status: DevicePreflightStatus) -> Color {
        switch status {
        case .blocked:
            return .red
        case .waiting:
            return .secondary
        case .ready:
            return .green
        }
    }
}
