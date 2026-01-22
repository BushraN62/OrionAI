import { useEffect, useRef } from 'react';

interface Star {
  x: number;
  y: number;
  z: number;
  size: number;
  speed: number;
  brightness: number;
  twinkleSpeed: number;
  twinkleOffset: number;
}

export const ParallaxStarfield = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mousePos = useRef({ x: 0.5, y: 0.5 });
  const stars = useRef<Star[]>([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const setCanvasSize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    setCanvasSize();
    window.addEventListener('resize', setCanvasSize);

    // Mouse move handler for parallax
    const handleMouseMove = (e: MouseEvent) => {
      mousePos.current = {
        x: e.clientX / window.innerWidth,
        y: e.clientY / window.innerHeight,
      };
    };
    window.addEventListener('mousemove', handleMouseMove);

    // Initialize stars with depth (z-axis for parallax)
    stars.current = Array.from({ length: 500 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      z: Math.random(), // depth 0-1
      size: Math.random() * 2.8 + 0.3,
      speed: Math.random() * 0.08 + 0.01,
      brightness: Math.random(),
      twinkleSpeed: Math.random() * 0.03 + 0.008,
      twinkleOffset: Math.random() * Math.PI * 2,
    }));

    let animationFrameId: number;
    let time = 0;

    const drawStar = (star: Star, brightness: number, parallaxX: number, parallaxY: number) => {
      if (!ctx) return;
      
      const alpha = brightness * 0.9;
      const parallaxFactor = star.z * 0.5;
      const x = star.x + parallaxX * parallaxFactor * 30;
      const y = star.y + parallaxY * parallaxFactor * 30;
      
      ctx.save();
      ctx.translate(x, y);
      
      // Color varies by brightness and depth
      const color = brightness > 0.7 
        ? `rgba(200, 220, 255, ${alpha})`
        : star.z > 0.6
        ? `rgba(180, 200, 255, ${alpha})`
        : `rgba(150, 180, 255, ${alpha * 0.9})`;
      
      ctx.fillStyle = color;
      
      // 4-pointed star with glow
      ctx.beginPath();
      for (let i = 0; i < 4; i++) {
        const angle = (i * Math.PI) / 2;
        const length = star.size;
        ctx.lineTo(
          Math.cos(angle) * length,
          Math.sin(angle) * length
        );
        const innerAngle = angle + Math.PI / 4;
        const innerLength = star.size * 0.4;
        ctx.lineTo(
          Math.cos(innerAngle) * innerLength,
          Math.sin(innerAngle) * innerLength
        );
      }
      ctx.closePath();
      ctx.fill();
      
      // Add glow for brighter stars
      if (brightness > 0.7) {
        ctx.shadowBlur = 8;
        ctx.shadowColor = color;
        ctx.fill();
      }
      
      ctx.restore();
    };

    const animate = () => {
      // Clear with gradient trail for smooth motion
      ctx.fillStyle = 'rgba(15, 15, 26, 0.12)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      time += 0.016;

      // Parallax offset based on mouse position (centered)
      const parallaxX = (mousePos.current.x - 0.5) * 2;
      const parallaxY = (mousePos.current.y - 0.5) * 2;

      stars.current.forEach((star) => {
        // Enhanced twinkle with occasional sparkle bursts
        const twinkle = Math.sin(time * star.twinkleSpeed + star.twinkleOffset);
        let brightness = star.brightness + twinkle * 0.5;
        
        // Random sparkle bursts (more frequent for closer stars)
        if (Math.random() > 0.998 - star.z * 0.001) {
          brightness = Math.min(1.2, brightness + 0.6);
        }
        
        // Pulsing size with depth influence
        const sizeMult = 0.8 + Math.abs(twinkle) * 0.5;
        const depthSize = 0.5 + star.z * 0.5;
        const currentStar = { ...star, size: star.size * sizeMult * depthSize };
        
        drawStar(currentStar, brightness, parallaxX, parallaxY);

        // Drift with depth-based speed
        star.y += star.speed * (1 + star.z * 0.5);
        if (star.y > canvas.height + 20) {
          star.y = -20;
          star.x = Math.random() * canvas.width;
        }
      });

      animationFrameId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', setCanvasSize);
      window.removeEventListener('mousemove', handleMouseMove);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none"
      style={{ 
        background: 'radial-gradient(ellipse at center, #1a1a2e 0%, #0f0f1a 70%, #0a0a12 100%)'
      }}
    />
  );
};
