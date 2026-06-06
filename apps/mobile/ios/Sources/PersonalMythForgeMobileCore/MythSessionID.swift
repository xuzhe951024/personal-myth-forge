public enum MythSessionID {
    public static func isValid(_ value: String) -> Bool {
        let prefix = "myth_"
        guard value.hasPrefix(prefix), value.count == prefix.count + 16 else {
            return false
        }
        return value.dropFirst(prefix.count).allSatisfy { character in
            ("0"..."9").contains(character) || ("a"..."f").contains(character)
        }
    }
}
