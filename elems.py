import streamlit as st

font_base = """
<style>
.deck-font {
    font-size: 32px !important;
}
.pilot-font {
    font-size: 28px !important;
    color: #6d3fc0 !important;
}
.game-data-font {
    font-size: 28px !important;
    color: #424242 !important;
}
.plain-font {
    font-size: 26px !important;
}
.plain-italic-font {
    font-size: 26px !important;
    font-style: italic !important;  /* Make this font italic */
}
.hero-font {
    font-size: 26px !important;
    color: #60b4ff !important;
}
.villain-font {
    font-size: 26px !important;
    color: #ff4b4b !important;
}
.hero-italic-font {
    font-size: 26px !important;
    color: #60b4ff !important;
    font-style: italic !important;  /* Make this font italic */

}
.villain-italic-font {
    font-size: 26px !important;
    color: #ff4b4b !important;
    font-style: italic !important;  /* Make this font italic */

}
.big-hero-font {
    font-size: 36px !important;
    color: #60b4ff !important;
}
.big-villain-font {
    font-size: 36px !important;
    color: #ff4b4b !important;
}
.small-hero-font {
    font-size: 20px !important;
    color: #60b4ff !important;
}
.small-villain-font {
    font-size: 20px !important;
    color: #ff4b4b !important;
}
.CotA-font {
    font-size: 28px !important;
    color: #d92b34 !important;
}
.AoA-font {
    font-size: 28px !important;
    color: #259adb !important;
}
.WC-font {
    font-size: 28px !important;
    color: #ad39a5 !important;
}
.MM-font {
    font-size: 28px !important;
    color: #e94e76 !important;
}
.DT-font {
    font-size: 28px !important;
    color: #136697 !important;
}
.WoE-font {
    font-size: 28px !important;
    color: #0c9aa8 !important;
}
.GR-font {
    font-size: 28px !important;
    color: #0c4f7f !important;
}
.VM23-font {
    font-size: 28px !important;
    color: #838383 !important;
}
.VM24-font {
    font-size: 28px !important;
    color: #838383 !important;
}
.VM25-font {
    font-size: 28px !important;
    color: #838383 !important;
}
.amber-font {
    font-size: 26px !important;
    color: #f8df65 !important;
}
</style>
"""

