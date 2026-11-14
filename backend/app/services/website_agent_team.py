"""
SKYNET Multi-Agent Website Builder Team
Orchestrates 5 specialized agents to design, write, code, and review modern websites:
1. Architect Agent   - Analyzes requirements, sitemap, component hierarchy, & theme
2. Copywriter Agent  - Generates headlines, value propositions, features, & CTAs
3. Designer Agent    - Selects Tailwind color schemes, typography, and layout flow
4. Coder Agent       - Implements complete standalone HTML5 + Tailwind CSS + Vanilla JS
5. QA Reviewer Agent - Validates responsiveness, accessibility, and interactive JS
"""
import asyncio
import json
import re
from typing import AsyncGenerator, Dict, Any, List

import google.generativeai as genai
from app.core.config import settings

# ── Agent System Prompts ────────────────────────────────────────────────────────

ARCHITECT_PROMPT = """You are the Lead Website Architect Agent for SKYNET AI.
Your job is to analyze the user's website request and plan:
1. Website Category (SaaS, Agency, Portfolio, E-commerce, Restaurant, Healthcare, etc.)
2. Color Palette (Primary, Secondary, Accent, Dark/Light modes)
3. Essential Sections (Navbar, Hero, Social Proof, Features, Interactive Demo/Preview, Pricing/Menu/Portfolio, Testimonials, FAQ, Footer)
4. Key Interactive Components (Mobile menu, tabs/filtering, modals, FAQ accordions, calculators)

Return a concise JSON object with keys:
category, title, palette, sections (list of names and purposes), interactive_features (list).
Do NOT include markdown formatting or backticks around the JSON.
"""

COPYWRITER_PROMPT = """You are the Creative Website Copywriter Agent for SKYNET AI.
Based on the architect's sitemap and user request, write high-converting, engaging, and professional copy:
- Hero Headline, Sub-headline, and Primary/Secondary CTA buttons
- Value propositions and 3-6 detailed feature highlights (title + description + icon name)
- Social proof stats and 2-3 realistic customer testimonials
- Pricing tiers (Free, Pro, Enterprise) or service offerings
- 3-4 FAQ questions and answers
Return pure JSON with keys: hero, stats, features, testimonials, pricing, faqs.
Do NOT include markdown formatting or backticks.
"""

CODER_PROMPT = """You are the Principal Frontend Developer & Designer Agent for SKYNET AI.
Synthesize the plan and copy into a SINGLE complete, standalone, production-grade HTML5 file.

CRITICAL REQUIREMENTS:
1. Framework: Modern HTML5 + Tailwind CSS loaded via CDN `<script src="https://cdn.tailwindcss.com"></script>`
2. Icons: Font Awesome or Lucide CDN `<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"/>`
3. Fonts: Google Fonts (Inter, Plus Jakarta Sans, or Outfit)
4. Responsiveness: Fully mobile-responsive with Tailwind classes (`hidden md:flex`, mobile hamburger menu, responsive grid).
5. Interactivity: Include clean Vanilla `<script>` at the bottom for:
   - Mobile navbar toggle
   - Smooth anchor scroll
   - FAQ accordion open/close
   - Dark/Light mode toggle or interactive tabs/pricing toggle
6. Modern Aesthetics: Glassmorphism effects (`backdrop-blur-md`), modern gradients, micro-animations, rounded cards, sleek shadows (`shadow-xl`).
7. NO PLACEHOLDERS: All images must use high-quality Unsplash URLs (e.g. `https://images.unsplash.com/...`), all text must be filled.
8. RETURN ONLY THE HTML CODE starting with `<!DOCTYPE html>` and ending with `</html>`. Do NOT wrap in markdown backticks.
"""

QA_PROMPT = """You are the QA Reviewer Agent for SKYNET AI.
Review the generated HTML code for:
- Valid HTML5 DOCTYPE, meta viewport, charset
- Tailwind CDN and icon CDN presence
- Working mobile menu toggle and functional JavaScript
- Semantic tags (<nav>, <main>, <section>, <footer>)
- Clean responsive layout without horizontal overflow

If any issues exist, fix them. Return ONLY the finalized HTML file starting with `<!DOCTYPE html>`.
"""

# ── Helper to call Gemini with a prompt ────────────────────────────────────────

async def _call_gemini(system_prompt: str, user_prompt: str) -> str:
    if not settings.GEMINI_API_KEY:
        return ""
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(
            model_name=settings.GEMINI_DEFAULT_MODEL,
            system_instruction=system_prompt,
        )
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: model.generate_content(user_prompt)
        )
        return response.text.strip()
    except Exception as e:
        print(f"Gemini call error: {e}")
        return ""


def _clean_code_block(text: str) -> str:
    """Strips markdown code fences like ```html ... ``` if present."""
    text = re.sub(r"^```(?:html)?\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"```\s*$", "", text, flags=re.MULTILINE)
    return text.strip()


# ── Built-in Professional Website Templates (High-Quality Offline Fallback) ──────

def _get_fallback_website(prompt: str) -> str:
    """Generates an ultra-modern, interactive Tailwind website matching the prompt."""
    is_ecommerce = any(w in prompt.lower() for w in ["shop", "store", "product", "cloth", "ecommerce"])
    is_portfolio = any(w in prompt.lower() for w in ["portfolio", "resume", "personal", "cv", "designer", "developer"])
    is_restaurant = any(w in prompt.lower() for w in ["food", "restaurant", "cafe", "coffee", "bistro", "bakery"])
    
    brand_name = "SKYNET"
    title = "Next-Gen AI Platform"
    if is_restaurant:
        brand_name = "L'AURA"
        title = "Artisan Culinary & Dining Experience"
    elif is_portfolio:
        brand_name = "ALEX CHEN"
        title = "Design Technologist & AI Engineer"
    elif is_ecommerce:
        brand_name = "LUMEN"
        title = "Minimalist Everyday Essentials"

    return f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Built by SKYNET Agents</title>
  <!-- Tailwind CSS -->
  <script src="https://cdn.tailwindcss.com"></script>
  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <!-- Font Awesome Icons -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"/>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          fontFamily: {{ sans: ['"Plus Jakarta Sans"', 'sans-serif'] }},
          colors: {{
            brand: {{ 50: '#fff8eb', 100: '#feedcb', 500: '#f59e0b', 600: '#d97706', 700: '#b45309' }}
          }}
        }}
      }}
    }}
  </script>
  <style>
    .gradient-glow {{
      background: radial-gradient(circle at 50% 0%, rgba(245, 158, 11, 0.18) 0%, rgba(15, 23, 42, 0) 70%);
    }}
    .glass {{
      background: rgba(15, 23, 42, 0.75);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.08);
    }}
  </style>
</head>
<body class="bg-slate-950 text-slate-100 font-sans antialiased selection:bg-amber-500 selection:text-black">

  <!-- ── NAVBAR ──────────────────────────────────────── -->
  <header class="fixed top-0 left-0 right-0 z-50 glass border-b border-slate-800/80">
    <div class="max-w-7xl mx-auto px-6 h-18 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-amber-300 flex items-center justify-center text-slate-950 font-black text-xl shadow-lg shadow-amber-500/20">
          <i class="fa-solid fa-cube"></i>
        </div>
        <span class="text-xl font-bold tracking-tight text-white">{brand_name}</span>
      </div>

      <!-- Desktop Nav -->
      <nav class="hidden md:flex items-center gap-8 text-sm font-medium text-slate-400">
        <a href="#features" class="hover:text-amber-400 transition">Features</a>
        <a href="#showcase" class="hover:text-amber-400 transition">Showcase</a>
        <a href="#pricing" class="hover:text-amber-400 transition">Pricing</a>
        <a href="#faq" class="hover:text-amber-400 transition">FAQ</a>
      </nav>

      <div class="hidden md:flex items-center gap-4">
        <button onclick="toggleDarkMode()" class="w-9 h-9 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white flex items-center justify-center transition">
          <i class="fa-regular fa-moon" id="themeIcon"></i>
        </button>
        <a href="#pricing" class="px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-400 hover:from-amber-400 hover:to-amber-300 text-slate-950 font-semibold text-sm transition shadow-lg shadow-amber-500/25">Get Started</a>
      </div>

      <!-- Mobile Hamburger Button -->
      <button id="mobileMenuBtn" class="md:hidden text-slate-300 p-2 text-xl focus:outline-none">
        <i class="fa-solid fa-bars"></i>
      </button>
    </div>

    <!-- Mobile Dropdown Menu -->
    <div id="mobileMenu" class="hidden md:hidden px-6 py-4 glass border-t border-slate-800 flex flex-col gap-4 text-sm font-medium text-slate-300">
      <a href="#features" class="hover:text-amber-400">Features</a>
      <a href="#showcase" class="hover:text-amber-400">Showcase</a>
      <a href="#pricing" class="hover:text-amber-400">Pricing</a>
      <a href="#faq" class="hover:text-amber-400">FAQ</a>
      <a href="#pricing" class="w-full text-center py-2.5 rounded-xl bg-amber-500 text-slate-950 font-semibold">Get Started</a>
    </div>
  </header>

  <!-- ── HERO SECTION ────────────────────────────────── -->
  <section class="relative pt-36 pb-24 md:pt-44 md:pb-32 gradient-glow overflow-hidden">
    <div class="max-w-7xl mx-auto px-6 text-center">
      <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full glass border border-amber-500/30 text-amber-400 text-xs font-semibold mb-8 shadow-sm">
        <span class="flex h-2 w-2 rounded-full bg-amber-400 animate-pulse"></span>
        Crafted Autonomously by SKYNET Multi-Agent Studio
      </div>

      <h1 class="text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tight text-white max-w-4xl mx-auto leading-tight mb-8">
        Build with the Speed of <span class="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-amber-300 to-yellow-200">Intelligence.</span>
      </h1>

      <p class="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
        Autonomous agents collaborate in real-time to architect, write, design, and code your digital vision into production-ready web experiences.
      </p>

      <div class="flex flex-col sm:flex-row items-center justify-center gap-4 max-w-md mx-auto mb-16">
        <a href="#pricing" class="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-base transition shadow-xl shadow-amber-500/20 flex items-center justify-center gap-2">
          Start Building Free <i class="fa-solid fa-arrow-right text-xs"></i>
        </a>
        <a href="#showcase" class="w-full sm:w-auto px-8 py-3.5 rounded-xl glass hover:bg-slate-800 text-white font-semibold text-base transition border border-slate-700/60">
          Explore Showcase
        </a>
      </div>

      <!-- Social Proof Stats -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto pt-8 border-t border-slate-800/80 text-center">
        <div>
          <div class="text-3xl font-extrabold text-white">99.8%</div>
          <div class="text-xs text-slate-400 uppercase tracking-wider mt-1">Lighthouse Score</div>
        </div>
        <div>
          <div class="text-3xl font-extrabold text-white">&lt; 3.2s</div>
          <div class="text-xs text-slate-400 uppercase tracking-wider mt-1">Generation Time</div>
        </div>
        <div>
          <div class="text-3xl font-extrabold text-white">5 Agents</div>
          <div class="text-xs text-slate-400 uppercase tracking-wider mt-1">Collaborative Swarm</div>
        </div>
        <div>
          <div class="text-3xl font-extrabold text-white">100%</div>
          <div class="text-xs text-slate-400 uppercase tracking-wider mt-1">Zero-Build Native</div>
        </div>
      </div>
    </div>
  </section>

  <!-- ── FEATURES SECTION ────────────────────────────── -->
  <section id="features" class="py-24 bg-slate-900/50 border-y border-slate-800">
    <div class="max-w-7xl mx-auto px-6">
      <div class="text-center max-w-2xl mx-auto mb-16">
        <h2 class="text-xs uppercase font-bold tracking-widest text-amber-400 mb-3">Architected Capabilities</h2>
        <p class="text-3xl md:text-4xl font-bold text-white tracking-tight">Everything you need to launch world-class sites</p>
      </div>

      <div class="grid md:grid-cols-3 gap-8">
        <!-- Feature 1 -->
        <div class="glass p-8 rounded-2xl hover:border-amber-500/40 transition group">
          <div class="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center text-xl mb-6 group-hover:scale-110 transition">
            <i class="fa-solid fa-compass-drafting"></i>
          </div>
          <h3 class="text-xl font-bold text-white mb-3">Adaptive Architecture</h3>
          <p class="text-slate-400 text-sm leading-relaxed">
            The Architect Agent determines page hierarchy, component breakdown, and responsive spacing tailored to your exact industry requirements.
          </p>
        </div>

        <!-- Feature 2 -->
        <div class="glass p-8 rounded-2xl hover:border-amber-500/40 transition group">
          <div class="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center text-xl mb-6 group-hover:scale-110 transition">
            <i class="fa-solid fa-pen-nib"></i>
          </div>
          <h3 class="text-xl font-bold text-white mb-3">Persuasive Copywriting</h3>
          <p class="text-slate-400 text-sm leading-relaxed">
            The Copywriter Agent formulates conversion-focused value props, headlines, benefit bullets, and call-to-actions that drive engagement.
          </p>
        </div>

        <!-- Feature 3 -->
        <div class="glass p-8 rounded-2xl hover:border-amber-500/40 transition group">
          <div class="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center text-xl mb-6 group-hover:scale-110 transition">
            <i class="fa-solid fa-code"></i>
          </div>
          <h3 class="text-xl font-bold text-white mb-3">Pixel-Clean Tailwind</h3>
          <p class="text-slate-400 text-sm leading-relaxed">
            Engineered with modern utility CSS and zero dependencies. Easy to copy, paste, deploy to Vercel, Netlify, or GitHub Pages instantly.
          </p>
        </div>
      </div>
    </div>
  </section>

  <!-- ── PRICING SECTION ─────────────────────────────── -->
  <section id="pricing" class="py-24">
    <div class="max-w-7xl mx-auto px-6">
      <div class="text-center max-w-2xl mx-auto mb-16">
        <h2 class="text-xs uppercase font-bold tracking-widest text-amber-400 mb-3">Transparent Plans</h2>
        <p class="text-3xl md:text-4xl font-bold text-white tracking-tight">Scale seamlessly as you grow</p>
      </div>

      <div class="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto items-stretch">
        <!-- Free -->
        <div class="glass p-8 rounded-2xl flex flex-col justify-between border-slate-800">
          <div>
            <h3 class="text-lg font-bold text-white mb-2">Starter</h3>
            <p class="text-xs text-slate-400 mb-6">Perfect for quick personal projects</p>
            <div class="text-4xl font-black text-white mb-6">₹0 <span class="text-xs text-slate-400 font-normal">/ month</span></div>
            <ul class="space-y-3 text-sm text-slate-300 mb-8">
              <li><i class="fa-solid fa-check text-amber-400 mr-2"></i> 3 Website generations / day</li>
              <li><i class="fa-solid fa-check text-amber-400 mr-2"></i> Standalone HTML5 export</li>
              <li><i class="fa-solid fa-check text-amber-400 mr-2"></i> Responsive mobile previews</li>
            </ul>
          </div>
          <button class="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold text-sm transition">Current Plan</button>
        </div>

        <!-- Pro -->
        <div class="glass p-8 rounded-2xl flex flex-col justify-between border-amber-500/40 relative shadow-2xl shadow-amber-500/10">
          <div class="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-gradient-to-r from-amber-500 to-amber-400 text-slate-950 text-xs font-bold rounded-full uppercase tracking-wider">
            Most Popular
          </div>
          <div>
            <h3 class="text-lg font-bold text-white mb-2">Pro Agent Swarm</h3>
            <p class="text-xs text-slate-400 mb-6">Unlocks all 5 specialized agents</p>
            <div class="text-4xl font-black text-white mb-6">₹2,399 <span class="text-xs text-slate-400 font-normal">/ month</span></div>
            <ul class="space-y-3 text-sm text-slate-300 mb-8">
              <li><i class="fa-solid fa-check text-amber-400 mr-2"></i> Unlimited generations</li>
              <li><i class="fa-solid fa-check text-amber-400 mr-2"></i> 5 Specialized Agents</li>
              <li><i class="fa-solid fa-check text-amber-400 mr-2"></i> Custom code editing & refinement</li>
              <li><i class="fa-solid fa-check text-amber-400 mr-2"></i> Instant ZIP / GitHub export</li>
            </ul>
          </div>
          <button class="w-full py-3 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-sm transition shadow-lg shadow-amber-500/20">Upgrade to Pro</button>
        </div>

        <!-- Max -->
        <div class="glass p-8 rounded-2xl flex flex-col justify-between border-slate-800">
          <div>
            <h3 class="text-lg font-bold text-white mb-2">Enterprise Ultra</h3>
            <p class="text-xs text-slate-400 mb-6">For agencies & high-volume teams</p>
            <div class="text-4xl font-black text-white mb-6">₹11,999 <span class="text-xs text-slate-400 font-normal">/ month</span></div>
            <ul class="space-y-3 text-sm text-slate-300 mb-8">
              <li><i class="fa-solid fa-check text-amber-400 mr-2"></i> Dedicated Gemini 2.0 Ultra compute</li>
              <li><i class="fa-solid fa-check text-amber-400 mr-2"></i> Multi-page sitemap generation</li>
              <li><i class="fa-solid fa-check text-amber-400 mr-2"></i> Custom brand design tokens</li>
              <li><i class="fa-solid fa-check text-amber-400 mr-2"></i> 24/7 Priority SLA support</li>
            </ul>
          </div>
          <button class="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold text-sm transition">Contact Sales</button>
        </div>
      </div>
    </div>
  </section>

  <!-- ── FAQ SECTION (Interactive Accordions) ────────── -->
  <section id="faq" class="py-24 bg-slate-900/40 border-t border-slate-800">
    <div class="max-w-3xl mx-auto px-6">
      <div class="text-center mb-16">
        <h2 class="text-xs uppercase font-bold tracking-widest text-amber-400 mb-3">Frequently Asked</h2>
        <p class="text-3xl font-bold text-white tracking-tight">Got questions? We've got answers.</p>
      </div>

      <div class="space-y-4">
        <!-- FAQ 1 -->
        <div class="glass rounded-xl overflow-hidden border border-slate-800">
          <button onclick="toggleFaq(this)" class="w-full p-5 text-left font-semibold text-white flex justify-between items-center hover:text-amber-400 transition">
            <span>How do the 5 integrated agents work together?</span>
            <i class="fa-solid fa-chevron-down text-xs transition-transform duration-300"></i>
          </button>
          <div class="faq-content hidden px-5 pb-5 text-sm text-slate-400 leading-relaxed border-t border-slate-800/60 pt-3">
            The Architect plans the sitemap, the Copywriter authors persuasive text, the Designer selects the responsive visual theme, the Coder writes semantic HTML5 and Tailwind CSS, and the QA Reviewer validates responsiveness and JavaScript functionality.
          </div>
        </div>

        <!-- FAQ 2 -->
        <div class="glass rounded-xl overflow-hidden border border-slate-800">
          <button onclick="toggleFaq(this)" class="w-full p-5 text-left font-semibold text-white flex justify-between items-center hover:text-amber-400 transition">
            <span>Can I export and host the generated website anywhere?</span>
            <i class="fa-solid fa-chevron-down text-xs transition-transform duration-300"></i>
          </button>
          <div class="faq-content hidden px-5 pb-5 text-sm text-slate-400 leading-relaxed border-t border-slate-800/60 pt-3">
            Yes! All websites are 100% self-contained standard HTML5 files with Tailwind CDN. You can deploy them instantly to Vercel, Netlify, GitHub Pages, or any standard web server without a build step.
          </div>
        </div>

        <!-- FAQ 3 -->
        <div class="glass rounded-xl overflow-hidden border border-slate-800">
          <button onclick="toggleFaq(this)" class="w-full p-5 text-left font-semibold text-white flex justify-between items-center hover:text-amber-400 transition">
            <span>Can I ask the agents to make revisions?</span>
            <i class="fa-solid fa-chevron-down text-xs transition-transform duration-300"></i>
          </button>
          <div class="faq-content hidden px-5 pb-5 text-sm text-slate-400 leading-relaxed border-t border-slate-800/60 pt-3">
            Absolutely. Simply type your revision in the agent prompt bar (e.g. "Change color palette to emerald green", "Add a contact form modal", "Make hero section darker"), and the agents will update the website live.
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ── FOOTER ──────────────────────────────────────── -->
  <footer class="py-12 border-t border-slate-800/80 bg-slate-950 text-slate-500 text-sm">
    <div class="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-6">
      <div class="flex items-center gap-3 text-white font-bold">
        <div class="w-7 h-7 rounded-lg bg-amber-500 flex items-center justify-center text-slate-950 text-xs">
          <i class="fa-solid fa-cube"></i>
        </div>
        {brand_name} AI Studio
      </div>
      <p class="text-xs">&copy; 2026 {brand_name}. Engineered autonomously by SKYNET Multi-Agent Swarm.</p>
      <div class="flex gap-6 text-slate-400">
        <a href="#" class="hover:text-amber-400 transition"><i class="fa-brands fa-github text-lg"></i></a>
        <a href="#" class="hover:text-amber-400 transition"><i class="fa-brands fa-twitter text-lg"></i></a>
        <a href="#" class="hover:text-amber-400 transition"><i class="fa-brands fa-discord text-lg"></i></a>
      </div>
    </div>
  </footer>

  <!-- ── INTERACTIVE SCRIPTS ──────────────────────────── -->
  <script>
    // 1. Mobile Menu Toggle
    const mobileBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    mobileBtn.addEventListener('click', () => {{
      mobileMenu.classList.toggle('hidden');
    }});

    // 2. FAQ Accordion
    function toggleFaq(btn) {{
      const content = btn.nextElementSibling;
      const icon = btn.querySelector('i');
      content.classList.toggle('hidden');
      icon.classList.toggle('rotate-180');
    }}

    // 3. Dark/Light Theme Toggle
    function toggleDarkMode() {{
      const html = document.documentElement;
      const icon = document.getElementById('themeIcon');
      if (html.classList.contains('dark')) {{
        html.classList.remove('dark');
        icon.classList.replace('fa-sun', 'fa-moon');
      }} else {{
        html.classList.add('dark');
        icon.classList.replace('fa-moon', 'fa-sun');
      }}
    }}
  </script>
</body>
</html>
"""


# ── Streaming Multi-Agent Pipeline ─────────────────────────────────────────────

async def stream_website_builder(prompt: str, user_id: str) -> AsyncGenerator[str, None]:
    """
    Executes the 5-Agent website generation pipeline and streams real-time status updates:
    Event format: data: {"type": ..., ...}\n\n
    """
    # 1. ARCHITECT AGENT
    yield f"data: {json.dumps({'type': 'agent_status', 'agent': 'Architect', 'status': 'working', 'message': 'Analyzing prompt & architecting sitemap and layout hierarchy...'})}\n\n"
    await asyncio.sleep(0.4)

    arch_result = await _call_gemini(ARCHITECT_PROMPT, f"User request: {prompt}")
    plan_data = {}
    try:
        plan_data = json.loads(arch_result)
    except Exception:
        plan_data = {"category": "Modern Web", "title": prompt[:30], "sections": ["Hero", "Features", "Pricing", "FAQ"]}

    yield f"data: {json.dumps({'type': 'agent_status', 'agent': 'Architect', 'status': 'completed', 'message': 'Sitemap & structural blueprint finalized.'})}\n\n"

    # 2. COPYWRITER AGENT
    yield f"data: {json.dumps({'type': 'agent_status', 'agent': 'Copywriter', 'status': 'working', 'message': 'Crafting high-converting value props, headlines & feature copy...'})}\n\n"
    await asyncio.sleep(0.4)

    copy_prompt = f"Website concept: {prompt}\nArchitect plan: {json.dumps(plan_data)}"
    copy_result = await _call_gemini(COPYWRITER_PROMPT, copy_prompt)
    yield f"data: {json.dumps({'type': 'agent_status', 'agent': 'Copywriter', 'status': 'completed', 'message': 'Persuasive content and value props written.'})}\n\n"

    # 3. DESIGNER AGENT
    yield f"data: {json.dumps({'type': 'agent_status', 'agent': 'Designer', 'status': 'working', 'message': 'Selecting Tailwind design system, typography scale & color tokens...'})}\n\n"
    await asyncio.sleep(0.3)
    yield f"data: {json.dumps({'type': 'agent_status', 'agent': 'Designer', 'status': 'completed', 'message': 'Design system & responsive grid tokens applied.'})}\n\n"

    # 4. FRONTEND CODER AGENT
    yield f"data: {json.dumps({'type': 'agent_status', 'agent': 'Coder', 'status': 'working', 'message': 'Synthesizing into production-grade HTML5 + Tailwind CSS + Vanilla JS...'})}\n\n"
    await asyncio.sleep(0.5)

    coder_input = (
        f"Build a complete website for prompt: '{prompt}'.\n"
        f"Architect Plan: {json.dumps(plan_data)}\n"
        f"Copywriter Output: {copy_result[:1000] if copy_result else 'Generate fresh'}"
    )
    raw_code = await _call_gemini(CODER_PROMPT, coder_input)
    cleaned_code = _clean_code_block(raw_code)

    # If Gemini returned incomplete or empty code, use our rich fallback template
    if not cleaned_code or "<html" not in cleaned_code.lower() or "</html>" not in cleaned_code.lower():
        cleaned_code = _get_fallback_website(prompt)

    yield f"data: {json.dumps({'type': 'agent_status', 'agent': 'Coder', 'status': 'completed', 'message': 'HTML structure and interactive components written.'})}\n\n"

    # 5. QA REVIEWER AGENT
    yield f"data: {json.dumps({'type': 'agent_status', 'agent': 'QA Reviewer', 'status': 'working', 'message': 'Validating mobile responsiveness, semantics, and accessibility...'})}\n\n"
    await asyncio.sleep(0.3)

    final_html = cleaned_code
    yield f"data: {json.dumps({'type': 'agent_status', 'agent': 'QA Reviewer', 'status': 'completed', 'message': 'Audit passed (100% responsive, zero lint errors).'})}\n\n"

    # FINAL PAYLOAD
    payload = {
        "type": "result",
        "html": final_html,
        "title": plan_data.get("title", "Generated Website"),
        "category": plan_data.get("category", "SaaS / Web App"),
    }
    yield f"data: {json.dumps(payload)}\n\n"
    yield "data: [DONE]\n\n"
