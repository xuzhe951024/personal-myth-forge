import SwiftUI

struct DemoSnapshotStatusView: View {
    let restoredTitle: String?
    let savedAt: String?
    let tickCount: Int
    let statusText: String?
    let backendHistoryStatusText: String?
    let isSyncingBackendHistory: Bool
    let clearSnapshot: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(alignment: .firstTextBaseline) {
                VStack(alignment: .leading, spacing: 2) {
                    Text(restoredTitle == nil ? "Demo Run" : "Restored Demo Run")
                        .font(.headline)
                    if let restoredTitle {
                        Text(restoredTitle)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
                Spacer()
                if restoredTitle != nil {
                    Button("Clear", action: clearSnapshot)
                        .buttonStyle(.bordered)
                        .controlSize(.small)
                }
            }

            if let savedAt {
                Text("Saved \(savedAt) - \(tickCount) NPC ticks")
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }

            if let statusText {
                Text(statusText)
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }

            if isSyncingBackendHistory {
                HStack(spacing: 6) {
                    ProgressView()
                        .controlSize(.small)
                    Text("Syncing backend history")
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                }
            }

            if let backendHistoryStatusText {
                Text(backendHistoryStatusText)
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }
        }
        .padding(10)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(.thinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
    }
}
