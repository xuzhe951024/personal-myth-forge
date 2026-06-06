import PersonalMythForgeMobileCore
import SwiftUI

struct DemoScriptView: View {
    let script: DemoScript

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .firstTextBaseline) {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Demo Script")
                        .font(.headline)
                    Text(script.nextAction)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .lineLimit(2)
                }
                Spacer()
                Text(currentBadge)
                    .font(.caption2.weight(.bold))
                    .foregroundStyle(.secondary)
            }

            VStack(alignment: .leading, spacing: 6) {
                ForEach(script.steps, id: \.id) { step in
                    HStack(alignment: .firstTextBaseline, spacing: 8) {
                        Text(symbol(for: step.status))
                            .font(.caption.weight(.bold))
                            .foregroundStyle(color(for: step.status))
                            .frame(width: 16, alignment: .leading)
                        Text(step.label)
                            .font(.caption.weight(.semibold))
                            .frame(width: 104, alignment: .leading)
                        Text(step.detail)
                            .font(.caption2)
                            .foregroundStyle(.secondary)
                            .lineLimit(2)
                        Spacer(minLength: 0)
                    }
                }
            }
        }
        .padding(10)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(.thinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
    }

    private var currentBadge: String {
        if script.steps.contains(where: { $0.status == .blocked }) {
            return "CHECK"
        }
        if script.steps.contains(where: { $0.status == .current }) {
            return "NEXT"
        }
        return "READY"
    }

    private func symbol(for status: DemoScriptStepStatus) -> String {
        switch status {
        case .waiting:
            return "-"
        case .current:
            return ">"
        case .complete:
            return "*"
        case .optional:
            return "+"
        case .blocked:
            return "!"
        }
    }

    private func color(for status: DemoScriptStepStatus) -> Color {
        switch status {
        case .waiting:
            return .secondary
        case .current:
            return .blue
        case .complete:
            return .green
        case .optional:
            return .cyan
        case .blocked:
            return .orange
        }
    }
}
