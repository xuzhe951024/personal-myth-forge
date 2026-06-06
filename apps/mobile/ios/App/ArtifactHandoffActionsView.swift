import PersonalMythForgeMobileCore
import SwiftUI

struct ArtifactHandoffActionsView: View {
    let summary: ArtifactHandoffActionSummary
    let cachedURL: URL?
    let retry: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(alignment: .firstTextBaseline) {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Artifact Handoff")
                        .font(.subheadline.weight(.semibold))
                    Text(summary.detail)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .lineLimit(2)
                }
                Spacer(minLength: 8)
                Text(statusBadge)
                    .font(.caption2.weight(.bold))
                    .foregroundStyle(statusColor)
            }

            ForEach(summary.actions, id: \.kind) { action in
                actionRow(action)
            }
        }
        .padding(10)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.secondary.opacity(0.08))
        .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
    }

    @ViewBuilder
    private func actionRow(_ action: ArtifactHandoffAction) -> some View {
        switch action.kind {
        case .shareCachedAsset where action.isEnabled && cachedURL != nil:
            ShareLink(item: cachedURL!) {
                Label(action.title, systemImage: iconName(for: action))
                    .font(.caption.weight(.semibold))
            }
            Text(action.detail)
                .font(.caption2)
                .foregroundStyle(.secondary)
                .lineLimit(1)
        case .retryDownload where action.isEnabled:
            Button(action: retry) {
                Label("Retry Download", systemImage: iconName(for: action))
            }
            .font(.caption.weight(.semibold))
            .buttonStyle(.bordered)
            Text(action.detail)
                .font(.caption2)
                .foregroundStyle(.secondary)
                .lineLimit(2)
        default:
            HStack(alignment: .firstTextBaseline, spacing: 8) {
                Image(systemName: iconName(for: action))
                    .font(.caption)
                    .foregroundStyle(color(for: action))
                    .frame(width: 16)
                VStack(alignment: .leading, spacing: 2) {
                    Text(action.title)
                        .font(.caption.weight(action.isPrimary ? .semibold : .regular))
                    Text(action.detail)
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                        .lineLimit(2)
                }
            }
        }
    }

    private var statusBadge: String {
        if summary.canOpenScene {
            return "SCENE"
        }
        if summary.canShareCachedAsset {
            return "CACHED"
        }
        if summary.actions.contains(where: { $0.status == .attention }) {
            return "ACTION"
        }
        return "WAIT"
    }

    private var statusColor: Color {
        if summary.canOpenScene || summary.canShareCachedAsset {
            return .green
        }
        if summary.actions.contains(where: { $0.status == .attention }) {
            return .orange
        }
        return .secondary
    }

    private func iconName(for action: ArtifactHandoffAction) -> String {
        switch action.kind {
        case .openScene:
            return "cube.transparent"
        case .shareCachedAsset:
            return "square.and.arrow.up"
        case .convertRequired:
            return "arrow.triangle.2.circlepath"
        case .retryDownload:
            return "arrow.clockwise"
        case .waiting:
            return "clock"
        }
    }

    private func color(for action: ArtifactHandoffAction) -> Color {
        switch action.status {
        case .ready:
            return .green
        case .attention:
            return .orange
        case .waiting:
            return .secondary
        }
    }
}
