// KhulnaSoft Engineering Knowledge OS SDK (generated). Do not hand-edit.

public enum AecClient {
    public static let base = "https://khulnasoft.github.io/api"

    public static func resources() -> String {
        base + "/resources"
    }

    public static func resource(slug: String) -> String {
        base + "/resources/{slug}".replacingOccurrences(of: "{slug}", with: slug)
    }

    public static func twin(slug: String) -> String {
        base + "/resources/{slug}/twin".replacingOccurrences(of: "{slug}", with: slug)
    }

    public static func context(slug: String) -> String {
        base + "/resources/{slug}/context".replacingOccurrences(of: "{slug}", with: slug)
    }

    public static func recommendations(slug: String) -> String {
        base + "/resources/{slug}/recommendations".replacingOccurrences(of: "{slug}", with: slug)
    }

    public static func graph() -> String {
        base + "/graph"
    }

    public static func impact() -> String {
        base + "/impact"
    }

    public static func events() -> String {
        base + "/events"
    }

    public static func analytics() -> String {
        base + "/analytics"
    }

    public static func release() -> String {
        base + "/release"
    }

}
