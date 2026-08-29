import Image from "next/image";
import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="site-footer-inner">
        <div className="footer-brand">
          <p className="brand-vaani">Vaani</p>
          <Image src="/sarvam-logo.png" alt="sarvam" width={108} height={28} />
          <p className="footer-tagline">Speak to the agentic web.</p>
          <p className="footer-fine">
            Multilingual WebMCP experience on the same Sarvam MCP capability
            layer used by Cursor and Claude.
          </p>
        </div>
        <div className="footer-cols">
          <div>
            <h3>Product</h3>
            <Link href="/vaani">Vaani (WebMCP)</Link>
            <Link href="/playground">Voice Agent Playground</Link>
            <Link href="/">MCP setup</Link>
            <a href="https://www.sarvam.ai" target="_blank" rel="noopener noreferrer">
              Sarvam platform
            </a>
          </div>
          <div>
            <h3>APIs</h3>
            <a href="https://docs.sarvam.ai" target="_blank" rel="noopener noreferrer">
              Speech to Text
            </a>
            <a href="https://docs.sarvam.ai" target="_blank" rel="noopener noreferrer">
              Text to Speech
            </a>
            <a href="https://docs.sarvam.ai" target="_blank" rel="noopener noreferrer">
              Translation
            </a>
            <a href="https://docs.sarvam.ai" target="_blank" rel="noopener noreferrer">
              Models
            </a>
          </div>
          <div>
            <h3>Developers</h3>
            <a href="https://docs.sarvam.ai" target="_blank" rel="noopener noreferrer">
              Documentation
            </a>
            <a
              href="https://github.com/sarvamai/sarvam-mcp"
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub
            </a>
            <a
              href="https://dashboard.sarvam.ai/key-management"
              target="_blank"
              rel="noopener noreferrer"
            >
              API keys
            </a>
          </div>
        </div>
      </div>
      <div className="site-footer-legal">
        <span>MCP for developer agents · WebMCP for browser agents.</span>
        <a href="https://www.sarvam.ai" target="_blank" rel="noopener noreferrer">
          sarvam.ai
        </a>
      </div>
    </footer>
  );
}
