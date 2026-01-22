import { useEffect, useRef } from 'react';

interface Star {
  x: number;
  y: number;
  size: number;
  color: string;
  opacity: number;
  twinkleSpeed: number;
  twinklePhase: number;
  driftX: number;
  driftY: number;
  zDepth: number;
  isHero: boolean;
  sparkleOffset: number;
}

export function Starfield() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Configuration
    const config = {
      starCount: 200,
      heroStars: 12,
      sizes: { small: 1.5, medium: 3, large: 5 },
      colors: { white: '#FFFFFF', violet: '#A58CFF', cyan: '#5BA8FF' },
      driftSpeed: 0.2,
    };

    // Function to draw a star shape
    const drawStar = (
      cx: number,
      cy: number,
      spikes: number,
      outerRadius: number,
      innerRadius: number,
      opacity: number,
      color: string
    ) => {
      let rot = (Math.PI / 2) * 3;
      const step = Math.PI / spikes;

      ctx.beginPath();
      ctx.moveTo(cx, cy - outerRadius);

      for (let i = 0; i < spikes; i++) {
        let x = cx + Math.cos(rot) * outerRadius;
        let y = cy + Math.sin(rot) * outerRadius;
        ctx.lineTo(x, y);
        rot += step;

        x = cx + Math.cos(rot) * innerRadius;
        y = cy + Math.sin(rot) * innerRadius;
        ctx.lineTo(x, y);
        rot += step;
      }

      ctx.lineTo(cx, cy - outerRadius);
      ctx.closePath();

      // Fill star with glow based on color
      const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, outerRadius * 2);
      const r = parseInt(color.slice(1, 3), 16);
      const g = parseInt(color.slice(3, 5), 16);
      const b = parseInt(color.slice(5, 7), 16);
      
      gradient.addColorStop(0, `rgba(${r}, ${g}, ${b}, ${opacity})`);
      gradient.addColorStop(0.3, `rgba(${r}, ${g}, ${b}, ${opacity * 0.6})`);
      gradient.addColorStop(0.7, `rgba(${r}, ${g}, ${b}, ${opacity * 0.3})`);
      gradient.addColorStop(1, `rgba(${r}, ${g}, ${b}, 0)`);
      
      ctx.fillStyle = gradient;
      ctx.fill();

      // Add bright center
      ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${opacity})`;
      ctx.fill();
    };

    // Set canvas size
    const resizeCanvas = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const canvasWidth = window.innerWidth;
      const canvasHeight = window.innerHeight;
      
      canvas.width = canvasWidth * dpr;
      canvas.height = canvasHeight * dpr;
      canvas.style.width = canvasWidth + 'px';
      canvas.style.height = canvasHeight + 'px';
      
      ctx.scale(dpr, dpr);
      
      return { canvasWidth, canvasHeight };
    };

    const { canvasWidth, canvasHeight } = resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Create stars
    const stars: Star[] = [];
    const { starCount, heroStars, sizes, colors, driftSpeed } = config;
    
    // Regular stars
    for (let i = 0; i < starCount; i++) {
      const sizeType = Math.random();
      const size = sizeType < 0.6 ? sizes.small : (sizeType < 0.9 ? sizes.medium : sizes.large);
      
      const colorType = Math.random();
      const color = colorType < 0.65 ? colors.white : (colorType < 0.85 ? colors.violet : colors.cyan);
      
      stars.push({
        x: Math.random() * canvasWidth,
        y: Math.random() * canvasHeight,
        size: size,
        color: color,
        opacity: Math.random() * 0.6 + 0.3,
        twinkleSpeed: Math.random() * 0.02 + 0.01,
        twinklePhase: Math.random() * Math.PI * 2,
        driftX: (Math.random() - 0.5) * driftSpeed,
        driftY: (Math.random() - 0.5) * driftSpeed,
        zDepth: Math.random() * 0.8 + 0.2,
        isHero: false,
        sparkleOffset: Math.random() * Math.PI * 2
      });
    }
    
    // Hero stars (larger with glow)
    for (let i = 0; i < heroStars; i++) {
      const color = Math.random() < 0.5 ? colors.violet : colors.cyan;
      
      stars.push({
        x: Math.random() * canvasWidth,
        y: Math.random() * canvasHeight,
        size: Math.random() * 4 + 8,
        color: color,
        opacity: Math.random() * 0.4 + 0.4,
        twinkleSpeed: Math.random() * 0.015 + 0.008,
        twinklePhase: Math.random() * Math.PI * 2,
        driftX: (Math.random() - 0.5) * driftSpeed * 0.5,
        driftY: (Math.random() - 0.5) * driftSpeed * 0.5,
        zDepth: Math.random() * 0.5 + 0.5,
        isHero: true,
        sparkleOffset: Math.random() * Math.PI * 2
      });
    }

    // Render function
    const renderStarfield = () => {
      // Clear canvas
      ctx.clearRect(0, 0, canvasWidth, canvasHeight);
      
      // Draw gradient background
      const gradient = ctx.createLinearGradient(0, 0, 0, canvasHeight);
      gradient.addColorStop(0, '#020617'); // slate-950
      gradient.addColorStop(1, '#0f172a'); // slate-900
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvasWidth, canvasHeight);
      
      // Draw stars
      stars.forEach(star => {
        // Calculate twinkling with sine wave
        const twinkle = Math.sin(star.twinklePhase);
        
        // Add occasional sparkle bursts
        const sparkleChance = Math.sin(star.twinklePhase * 3 + star.sparkleOffset);
        const sparkle = sparkleChance > 0.95 ? 1.5 : 1;
        
        const baseOpacity = star.opacity * (0.3 + twinkle * 0.6);
        const currentOpacity = Math.min(1, baseOpacity * sparkle);
        
        if (star.isHero) {
          // Hero star with radial glow
          const gradient = ctx.createRadialGradient(star.x, star.y, 0, star.x, star.y, star.size);
          const r = parseInt(star.color.slice(1, 3), 16);
          const g = parseInt(star.color.slice(3, 5), 16);
          const b = parseInt(star.color.slice(5, 7), 16);
          gradient.addColorStop(0, `rgba(${r}, ${g}, ${b}, ${currentOpacity})`);
          gradient.addColorStop(0.5, `rgba(${r}, ${g}, ${b}, ${currentOpacity * 0.5})`);
          gradient.addColorStop(1, `rgba(${r}, ${g}, ${b}, 0)`);
          
          ctx.fillStyle = gradient;
          ctx.beginPath();
          ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
          ctx.fill();
        } else {
          // Regular star - draw star shape with size variation
          const sizeMultiplier = 0.8 + (twinkle * 0.5 + 0.5) * 0.4;
          const outerRadius = star.size * sizeMultiplier;
          const innerRadius = outerRadius * 0.4;
          
          drawStar(star.x, star.y, 4, outerRadius, innerRadius, currentOpacity, star.color);
        }
      });
    };

    // Animation loop
    let animationFrameId: number;
    
    const animate = () => {
      // Update star positions and twinkle
      stars.forEach(star => {
        star.twinklePhase += star.twinkleSpeed;
        star.x += star.driftX;
        star.y += star.driftY;
        
        // Wrap around screen edges
        if (star.x < -10) star.x = canvasWidth + 10;
        if (star.x > canvasWidth + 10) star.x = -10;
        if (star.y < -10) star.y = canvasHeight + 10;
        if (star.y > canvasHeight + 10) star.y = -10;
      });
      
      renderStarfield();
      animationFrameId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none"
      style={{ zIndex: 0 }}
    />
  );
}
