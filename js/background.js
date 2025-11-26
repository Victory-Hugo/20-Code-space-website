// Background animation based on dithered waves effect
const canvas = document.getElementById('background-canvas');
const ctx = canvas.getContext('2d');

let width, height;
let time = 0;
let mouseX = 0;
let mouseY = 0;
let pixelSize = 4;

// Configuration
const config = {
    waveSpeed: 0.05,
    waveFrequency: 3,
    waveAmplitude: 0.3,
    waveColor: [0.15, 0.18, 0.2], // Much darker blue-gray
    colorNum: 4,
    enableMouseInteraction: true,
    mouseRadius: 0.3
};

function resize() {
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;
}

// Perlin noise helper functions
function fade(t) {
    return t * t * t * (t * (t * 6 - 15) + 10);
}

function lerp(a, b, t) {
    return a + t * (b - a);
}

// Simplified noise function
const permutation = [];
for (let i = 0; i < 256; i++) {
    permutation[i] = Math.floor(Math.random() * 256);
}
for (let i = 0; i < 256; i++) {
    permutation[256 + i] = permutation[i];
}

function grad(hash, x, y) {
    const h = hash & 3;
    const u = h < 2 ? x : y;
    const v = h < 2 ? y : x;
    return ((h & 1) === 0 ? u : -u) + ((h & 2) === 0 ? v : -v);
}

function noise(x, y) {
    const X = Math.floor(x) & 255;
    const Y = Math.floor(y) & 255;
    
    x -= Math.floor(x);
    y -= Math.floor(y);
    
    const u = fade(x);
    const v = fade(y);
    
    const a = permutation[X] + Y;
    const aa = permutation[a];
    const ab = permutation[a + 1];
    const b = permutation[X + 1] + Y;
    const ba = permutation[b];
    const bb = permutation[b + 1];
    
    return lerp(
        lerp(grad(permutation[aa], x, y), grad(permutation[ba], x - 1, y), u),
        lerp(grad(permutation[ab], x, y - 1), grad(permutation[bb], x - 1, y - 1), u),
        v
    );
}

function fbm(x, y) {
    let value = 0;
    let amplitude = 1;
    let frequency = config.waveFrequency;
    
    for (let i = 0; i < 4; i++) {
        value += amplitude * Math.abs(noise(x * frequency, y * frequency));
        frequency *= 2;
        amplitude *= config.waveAmplitude;
    }
    
    return value;
}

function pattern(x, y, t) {
    const px = x - t * config.waveSpeed;
    const py = y - t * config.waveSpeed;
    return fbm(x + fbm(px, py), y + fbm(px, py));
}

// Bayer matrix for dithering
const bayerMatrix = [
    [0, 48, 12, 60, 3, 51, 15, 63],
    [32, 16, 44, 28, 35, 19, 47, 31],
    [8, 56, 4, 52, 11, 59, 7, 55],
    [40, 24, 36, 20, 43, 27, 39, 23],
    [2, 50, 14, 62, 1, 49, 13, 61],
    [34, 18, 46, 30, 33, 17, 45, 29],
    [10, 58, 6, 54, 9, 57, 5, 53],
    [42, 26, 38, 22, 41, 25, 37, 21]
].map(row => row.map(v => v / 64));

function dither(color, x, y) {
    const mx = Math.floor(x / pixelSize) % 8;
    const my = Math.floor(y / pixelSize) % 8;
    const threshold = bayerMatrix[my][mx] - 0.25;
    const step = 1 / (config.colorNum - 1);
    
    color += threshold * step;
    color = Math.max(0, Math.min(1, color - 0.2));
    
    return Math.round(color * (config.colorNum - 1)) / (config.colorNum - 1);
}

function render() {
    const imageData = ctx.createImageData(width, height);
    const data = imageData.data;
    
    for (let y = 0; y < height; y += pixelSize) {
        for (let x = 0; x < width; x += pixelSize) {
            // Normalize coordinates
            const nx = (x / width - 0.5) * 2;
            const ny = (y / height - 0.5) * 2;
            
            // Calculate pattern value
            let value = pattern(nx, ny, time);
            
            // Mouse interaction
            if (config.enableMouseInteraction) {
                const mx = (mouseX / width - 0.5) * 2;
                const my = (mouseY / height - 0.5) * 2;
                const dist = Math.sqrt((nx - mx) ** 2 + (ny - my) ** 2);
                const effect = Math.max(0, 1 - dist / config.mouseRadius);
                value -= 0.5 * effect;
            }
            
            // Apply dithering
            const r = dither(value * config.waveColor[0], x, y);
            const g = dither(value * config.waveColor[1], x, y);
            const b = dither(value * config.waveColor[2], x, y);
            
            // Fill pixelated square
            for (let py = 0; py < pixelSize && y + py < height; py++) {
                for (let px = 0; px < pixelSize && x + px < width; px++) {
                    const index = ((y + py) * width + (x + px)) * 4;
                    data[index] = r * 255;
                    data[index + 1] = g * 255;
                    data[index + 2] = b * 255;
                    data[index + 3] = 255;
                }
            }
        }
    }
    
    ctx.putImageData(imageData, 0, 0);
}

function animate() {
    time += 0.01;
    render();
    requestAnimationFrame(animate);
}

// Event listeners
window.addEventListener('resize', resize);

canvas.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
});

// Initialize
resize();
animate();
