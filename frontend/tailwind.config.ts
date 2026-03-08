import type { Config } from 'tailwindcss'
const config: Config = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: { extend: {
    fontFamily: { sans: ['Plus Jakarta Sans','sans-serif'], mono: ['JetBrains Mono','monospace'] },
    keyframes: {
      fadeUp: { from:{opacity:'0',transform:'translateY(6px)'}, to:{opacity:'1',transform:'none'} },
      slideIn:{ from:{opacity:'0',transform:'translateY(20px)'}, to:{opacity:'1',transform:'none'} },
    },
    animation: { 'fade-up':'fadeUp .18s ease', 'slide-in':'slideIn .2s ease' },
  }},
  plugins: [],
}
export default config
