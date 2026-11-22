from pathlib import Path
p=Path(__file__).parent/'frontend/public/avatars';p.mkdir(parents=True,exist_ok=True)
configs={
'fox':('#fb923c','#ffedd5','#9a3412','#fb7185','fox'),
'rabbit':('#d8b4fe','#fdf4ff','#7e22ce','#f472b6','rabbit'),
'penguin':('#64748b','#f1f5f9','#172554','#38bdf8','penguin'),
'turtle':('#4ade80','#dcfce7','#166534','#2dd4bf','turtle'),
'cat':('#facc15','#fef9c3','#854d0e','#fb7185','cat'),
'owl':('#c4b5fd','#ede9fe','#5b21b6','#a78bfa','owl')}
for key,(base,light,dark,accent,typ) in configs.items():
    ears=''
    if typ in ('fox','cat'):
      ears=f'<path d="M64 110 49 27 Q83 38 104 75 M176 110 191 27 Q157 38 136 75" fill="{base}" stroke="{dark}" stroke-width="6" stroke-linejoin="round"/><path d="M62 82 59 49 87 76 M178 82 181 49 153 76" fill="{accent}"/>'
    elif typ=='rabbit':
      ears=f'<ellipse cx="79" cy="48" rx="22" ry="51" fill="{base}" stroke="{dark}" stroke-width="5"/><ellipse cx="161" cy="48" rx="22" ry="51" fill="{base}" stroke="{dark}" stroke-width="5"/><ellipse cx="79" cy="45" rx="10" ry="35" fill="{accent}" opacity=".8"/><ellipse cx="161" cy="45" rx="10" ry="35" fill="{accent}" opacity=".8"/>'
    elif typ=='owl':
      ears=f'<path d="M52 106 43 35 94 66 M188 106 197 35 146 66" fill="{base}" stroke="{dark}" stroke-width="5"/>'
    elif typ=='turtle':
      ears=f'<ellipse cx="57" cy="128" rx="24" ry="30" fill="{base}"/><ellipse cx="183" cy="128" rx="24" ry="30" fill="{base}"/>'
    else:
      ears=f'<path d="M60 102 Q35 52 61 39 Q77 31 88 66 M180 102 Q205 52 179 39 Q163 31 152 66" fill="{dark}"/>'
    face=f'<ellipse cx="120" cy="135" rx="85" ry="88" fill="{base}" stroke="{dark}" stroke-width="5"/>'
    if typ=='penguin': face+=f'<ellipse cx="120" cy="148" rx="58" ry="68" fill="{light}"/>'
    elif typ=='fox': face+=f'<path d="M39 145 Q64 201 120 209 Q176 201 201 145 Q174 166 153 151 Q120 180 87 151 Q66 166 39 145" fill="{light}"/>'
    elif typ=='owl': face+=f'<ellipse cx="85" cy="134" rx="37" ry="45" fill="{light}"/><ellipse cx="155" cy="134" rx="37" ry="45" fill="{light}"/>'
    else: face+=f'<ellipse cx="120" cy="175" rx="49" ry="38" fill="{light}" opacity=".9"/>'
    beak=f'<path d="M109 159 131 159 120 178Z" fill="#f97316"/>' if typ in ('penguin','owl') else f'<path d="M111 159 Q120 151 129 159 Q120 174 111 159" fill="{dark}"/>'
    eyes=f'<ellipse cx="88" cy="132" rx="8" ry="12" fill="{dark}"/><ellipse cx="152" cy="132" rx="8" ry="12" fill="{dark}"/><circle cx="91" cy="128" r="3" fill="white"/><circle cx="155" cy="128" r="3" fill="white"/>'
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" role="img" aria-label="{key} avatar"><defs><radialGradient id="bg" cx="30%" cy="15%" r="90%"><stop stop-color="{light}"/><stop offset="1" stop-color="{accent}" stop-opacity=".4"/></radialGradient><linearGradient id="shine" x1="0" x2="1" y1="0" y2="1"><stop stop-color="white" stop-opacity=".7"/><stop offset="1" stop-color="white" stop-opacity="0"/></linearGradient></defs><circle cx="120" cy="120" r="116" fill="url(#bg)"/><circle cx="120" cy="120" r="112" fill="none" stroke="white" stroke-opacity=".7" stroke-width="5"/>{ears}{face}<ellipse cx="74" cy="157" rx="17" ry="9" fill="{accent}" opacity=".3"/><ellipse cx="166" cy="157" rx="17" ry="9" fill="{accent}" opacity=".3"/>{eyes}{beak}<path d="M109 181 Q120 191 131 181" stroke="{dark}" stroke-width="4" fill="none" stroke-linecap="round"/><ellipse cx="76" cy="62" rx="65" ry="26" transform="rotate(-35 76 62)" fill="url(#shine)" opacity=".35"/></svg>'''
    (p/f'{key}.svg').write_text(svg)
print('Wrote avatars',list(configs))
