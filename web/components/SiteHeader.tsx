import Image from "next/image";
import Link from "next/link";

export function SiteHeader() {
  return (
    <header className="site-header">
      <div className="site-header-inner">
        <Link href="/" className="brand">
          <span className="brand-vaani">Vaani</span>
          <Image
            src="/sarvam-logo.png"
            alt="powered by sarvam"
            width={108}
            height={28}
            priority
          />
        </Link>
        <nav className="site-nav" aria-label="Primary">
          <Link href="/vaani">WebMCP</Link>
          <Link href="/playground">Voice Agent</Link>
          <a href="https://docs.sarvam.ai" target="_blank" rel="noopener noreferrer">
            Developers
          </a>
          <a href="https://www.sarvam.ai" target="_blank" rel="noopener noreferrer">
            Platform
          </a>
          <a
            href="https://github.com/sarvamai/sarvam-mcp"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
          </a>
        </nav>
        <div className="site-header-actions">
          <a
            className="btn btn-ghost"
            href="https://dashboard.sarvam.ai"
            target="_blank"
            rel="noopener noreferrer"
          >
            Log In
          </a>
          <a
            className="btn btn-solid"
            href="https://dashboard.sarvam.ai/key-management"
            target="_blank"
            rel="noopener noreferrer"
          >
            Get API Key
          </a>
        </div>
      </div>
    </header>
  );
}
