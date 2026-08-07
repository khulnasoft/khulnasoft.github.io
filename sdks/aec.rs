//! KhulnaSoft Engineering Knowledge OS SDK (generated). Do not hand-edit.

const BASE: &str = "https://khulnasoft.github.io/api";

pub struct Client;

pub fn resources() -> String {
    format!("{}/resources", BASE)
}

pub fn resource(slug: &str) -> String {
    format!("{}/resources/{}", BASE, slug)
}

pub fn twin(slug: &str) -> String {
    format!("{}/resources/{}/twin", BASE, slug)
}

pub fn context(slug: &str) -> String {
    format!("{}/resources/{}/context", BASE, slug)
}

pub fn recommendations(slug: &str) -> String {
    format!("{}/resources/{}/recommendations", BASE, slug)
}

pub fn graph() -> String {
    format!("{}/graph", BASE)
}

pub fn impact() -> String {
    format!("{}/impact", BASE)
}

pub fn events() -> String {
    format!("{}/events", BASE)
}

pub fn analytics() -> String {
    format!("{}/analytics", BASE)
}

pub fn release() -> String {
    format!("{}/release", BASE)
}

