import PersonalMythForgeMobileCore
import SwiftUI

struct NPCTickView: View {
    let session: MythSession?
    let tick: NPCAgentTick?
    let summary: NPCAgentTickSummary
    let actionGate: NPCAgentActionGate
    let tickHistoryCount: Int
    let isLoading: Bool
    let isRunningAutonomy: Bool
    let errorMessage: String?
    let advanceVillage: () -> Void
    let runAutonomy: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .firstTextBaseline) {
                Text("Next Village Tick")
                    .font(.headline)
                Spacer()
                if let tick {
                    Text(tick.agentRuntime)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }

            agentSummary

            if tickHistoryCount > 0 {
                Text("\(tickHistoryCount) local ticks saved")
                    .font(.caption2.weight(.semibold))
                    .foregroundStyle(.secondary)
            }

            HStack(spacing: 8) {
                Button(action: advanceVillage) {
                    if isLoading {
                        ProgressView()
                    } else {
                        Text(actionGate.advanceTitle)
                    }
                }
                .buttonStyle(.borderedProminent)
                .disabled(!actionGate.canAdvanceVillage)

                Button(action: runAutonomy) {
                    if isRunningAutonomy {
                        ProgressView()
                    } else {
                        Text(actionGate.autonomyTitle)
                    }
                }
                .buttonStyle(.bordered)
                .disabled(!actionGate.canRunAutonomy)
            }

            Text(actionGate.detail)
                .font(.caption)
                .foregroundStyle(actionGate.disabledReason == nil ? Color.secondary : Color.orange)

            if let errorMessage {
                Text(errorMessage)
                    .font(.caption)
                    .foregroundStyle(.red)
            }

            if let tick {
                Text("Tick \(tick.tickIndex)")
                    .font(.subheadline.weight(.semibold))

                ForEach(tick.npcAgentTraces, id: \.npcId) { trace in
                    VStack(alignment: .leading, spacing: 4) {
                        HStack {
                            Text(trace.name)
                                .font(.subheadline.weight(.semibold))
                            Spacer()
                            Text(confidenceLabel(trace.confidence))
                                .font(.caption2.weight(.semibold))
                                .foregroundStyle(.secondary)
                        }
                        Text(trace.intention)
                            .font(.caption)
                        Text(trace.proposedAction)
                            .font(.caption.weight(.semibold))
                        Text(trace.rationale)
                            .font(.caption2)
                            .foregroundStyle(.secondary)
                    }
                    .padding(10)
                    .background(.secondary.opacity(0.08))
                    .clipShape(RoundedRectangle(cornerRadius: 8))
                }

                actionGroup(title: "Accepted", actions: tick.worldResolution.acceptedActions)
                actionGroup(title: "Rejected", actions: tick.worldResolution.rejectedActions)

                if !tick.worldResolution.visibleChanges.isEmpty {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Visible Changes")
                            .font(.subheadline.weight(.semibold))
                        ForEach(tick.worldResolution.visibleChanges, id: \.self) { change in
                            Text(change)
                                .font(.caption)
                        }
                    }
                }
            } else if session != nil {
                Text("Advance once the first village response is ready.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
    }

    private func actionGroup(title: String, actions: [ResolvedNPCAction]) -> some View {
        Group {
            if !actions.isEmpty {
                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.subheadline.weight(.semibold))
                    ForEach(actions, id: \.action) { action in
                        Text("\(action.action) - \(action.reason)")
                            .font(.caption)
                            .foregroundStyle(action.status == "accepted" ? .primary : .secondary)
                    }
                }
            }
        }
    }

    private var agentSummary: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(alignment: .firstTextBaseline) {
                VStack(alignment: .leading, spacing: 2) {
                    Text(summary.title)
                        .font(.subheadline.weight(.semibold))
                    Text(summary.detail)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .lineLimit(3)
                }
                Spacer(minLength: 8)
                Text(statusBadge)
                    .font(.caption2.weight(.bold))
                    .foregroundStyle(statusColor)
            }

            VStack(alignment: .leading, spacing: 4) {
                summaryMetric("Runtime", summary.runtimeLabel)
                summaryMetric("Tick", summary.tickLabel)
                summaryMetric("Decision", summary.decisionLabel)
            }

            if !summary.rows.isEmpty {
                VStack(alignment: .leading, spacing: 3) {
                    ForEach(summary.rows, id: \.self) { row in
                        Text(row)
                            .font(.caption2)
                            .foregroundStyle(.secondary)
                            .lineLimit(2)
                    }
                }
            }

            if !summary.privacyNotes.isEmpty {
                Text(summary.privacyNotes.joined(separator: " "))
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

    private func summaryMetric(_ label: String, _ value: String) -> some View {
        HStack(alignment: .firstTextBaseline, spacing: 8) {
            Text(label)
                .font(.caption2.weight(.semibold))
                .foregroundStyle(.secondary)
                .frame(width: 58, alignment: .leading)
            Text(value)
                .font(.caption.weight(.semibold))
                .lineLimit(2)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    private var statusBadge: String {
        switch summary.status {
        case .waiting:
            return "WAIT"
        case .running:
            return "RUN"
        case .ready:
            return "READY"
        case .needsAttention:
            return "CHECK"
        }
    }

    private var statusColor: Color {
        switch summary.status {
        case .waiting:
            return .secondary
        case .running:
            return .blue
        case .ready:
            return .green
        case .needsAttention:
            return .orange
        }
    }

    private func confidenceLabel(_ confidence: Double) -> String {
        "\(Int((confidence * 100).rounded()))%"
    }
}
