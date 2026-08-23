#!/usr/bin/env python3
"""Force the SSML root locale to match the selected fr-FR voice when supported."""
import re
try:
    import edge_tts.communicate as edge_communicate
    _original=getattr(edge_communicate,'mkssml',None)
    if _original:
        def _locale(voice):
            m=re.match(r'^([a-z]{2,3}-[A-Z]{2})-',voice or '') or re.search(r'\(([a-z]{2,3}-[A-Z]{2}),',voice or '')
            return m.group(1) if m else None
        def _localized(tc,escaped_text):
            ssml=_original(tc,escaped_text); locale=_locale(tc.voice)
            return re.sub(r"xml:lang=(['\"])en-US\1",f"xml:lang='{locale}'",ssml,count=1) if locale else ssml
        edge_communicate.mkssml=_localized
except Exception:
    pass
from render_audioguide import main
if __name__=='__main__': main()
