// Unified input: tap / click / Space / Up / W all call onFlap().
// Pause button clicks go to onPause() when tap falls inside a registered rect.

export class Input {
    constructor(canvas) {
        this.canvas = canvas;
        this.onFlap = () => {};
        this.onPause = () => {};
        this.onPointerAt = () => {}; // (vx, vy) in virtual pixels
        this.pauseRect = null; // {x,y,w,h} in virtual pixels
        this._bind();
    }

    setPauseRect(rect) { this.pauseRect = rect; }

    _toVirtual(evt) {
        const r = this.canvas.getBoundingClientRect();
        const px = (evt.clientX - r.left) * (this.canvas.width / r.width);
        const py = (evt.clientY - r.top) * (this.canvas.height / r.height);
        return { x: px, y: py };
    }

    _bind() {
        const tap = (evt) => {
            evt.preventDefault();
            const v = this._toVirtual(evt);
            this.onPointerAt(v.x, v.y);
            const pr = this.pauseRect;
            if (pr && v.x >= pr.x && v.x <= pr.x + pr.w && v.y >= pr.y && v.y <= pr.y + pr.h) {
                this.onPause();
                return;
            }
            this.onFlap();
        };
        this.canvas.addEventListener('pointerdown', tap, { passive: false });
        this.canvas.addEventListener('touchstart', (e) => e.preventDefault(), { passive: false });

        window.addEventListener('keydown', (e) => {
            if (e.repeat) return;
            if (e.code === 'Space' || e.code === 'ArrowUp' || e.code === 'KeyW') {
                e.preventDefault();
                this.onFlap();
            } else if (e.code === 'KeyP' || e.code === 'Escape') {
                e.preventDefault();
                this.onPause();
            }
        });
    }
}
