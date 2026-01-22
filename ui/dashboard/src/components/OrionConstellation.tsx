import { motion } from 'framer-motion';

export function OrionConstellation() {
  // Orion constellation matching the exact image pattern
  const stars = [
    // Top pentagon/shield shape (5 stars)
    { x: 80, y: 15, size: 4, color: '#8fb3ff', name: 'Top', glow: 'rgba(143,179,255,0.6)' },
    { x: 50, y: 40, size: 4, color: '#8fb3ff', name: 'TopLeft', glow: 'rgba(143,179,255,0.6)' },
    { x: 110, y: 40, size: 4, color: '#8fb3ff', name: 'TopRight', glow: 'rgba(143,179,255,0.6)' },
    { x: 45, y: 70, size: 4, color: '#8fb3ff', name: 'MidLeft', glow: 'rgba(143,179,255,0.6)' },
    { x: 115, y: 70, size: 4, color: '#8fb3ff', name: 'MidRight', glow: 'rgba(143,179,255,0.6)' },
    
    // Center star (Betelgeuse - reddish)
    { x: 40, y: 95, size: 7, color: '#ff8b6a', name: 'Betelgeuse', glow: 'rgba(255,139,106,0.7)' },
    
    // Belt stars (3 perfectly aligned)
    { x: 70, y: 95, size: 5, color: '#d4e8ff', name: 'BeltLeft', glow: 'rgba(212,232,255,0.6)' },
    { x: 90, y: 95, size: 5, color: '#d4e8ff', name: 'BeltCenter', glow: 'rgba(212,232,255,0.6)' },
    { x: 110, y: 95, size: 5, color: '#d4e8ff', name: 'BeltRight', glow: 'rgba(212,232,255,0.6)' },
    
    // Sword below belt (vertical line)
    { x: 90, y: 115, size: 3, color: '#b8d4ff', name: 'Sword1', glow: 'rgba(184,212,255,0.5)' },
    { x: 90, y: 130, size: 3, color: '#b8d4ff', name: 'Sword2', glow: 'rgba(184,212,255,0.5)' },
    
    // Bottom triangle (legs)
    { x: 50, y: 155, size: 5, color: '#8fb3ff', name: 'LeftFoot', glow: 'rgba(143,179,255,0.6)' },
    { x: 110, y: 155, size: 6, color: '#6eb3ff', name: 'Rigel', glow: 'rgba(110,179,255,0.7)' },
    
    // Left arm extension
    { x: 15, y: 75, size: 3, color: '#8fb3ff', name: 'LeftArm1', glow: 'rgba(143,179,255,0.5)' },
    { x: 10, y: 100, size: 3, color: '#8fb3ff', name: 'LeftArm2', glow: 'rgba(143,179,255,0.5)' },
    
    // Right arm extension  
    { x: 145, y: 75, size: 3, color: '#8fb3ff', name: 'RightArm1', glow: 'rgba(143,179,255,0.5)' },
    { x: 150, y: 100, size: 3, color: '#8fb3ff', name: 'RightArm2', glow: 'rgba(143,179,255,0.5)' },
  ];

  // Constellation lines matching the exact image geometry
  const lines = [
    // Top pentagon
    { x1: 80, y1: 15, x2: 50, y2: 40 },
    { x1: 80, y1: 15, x2: 110, y2: 40 },
    { x1: 50, y1: 40, x2: 45, y2: 70 },
    { x1: 110, y1: 40, x2: 115, y2: 70 },
    { x1: 45, y1: 70, x2: 115, y2: 70 }, // Bottom of pentagon
    
    // Left side body
    { x1: 45, y1: 70, x2: 40, y2: 95 }, // To Betelgeuse
    { x1: 40, y1: 95, x2: 50, y2: 155 }, // To left foot
    
    // Right side body
    { x1: 115, y1: 70, x2: 110, y2: 95 }, // To belt
    { x1: 110, y1: 95, x2: 110, y2: 155 }, // To Rigel
    
    // Belt horizontal
    { x1: 70, y1: 95, x2: 90, y2: 95 },
    { x1: 90, y1: 95, x2: 110, y2: 95 },
    
    // Sword (vertical below belt center)
    { x1: 90, y1: 95, x2: 90, y2: 115 },
    { x1: 90, y1: 115, x2: 90, y2: 130 },
    
    // Left arm
    { x1: 45, y1: 70, x2: 15, y2: 75 },
    { x1: 15, y1: 75, x2: 10, y2: 100 },
    { x1: 10, y1: 100, x2: 40, y2: 95 },
    
    // Right arm
    { x1: 115, y1: 70, x2: 145, y2: 75 },
    { x1: 145, y1: 75, x2: 150, y2: 100 },
    { x1: 150, y1: 100, x2: 110, y2: 95 },
    
    // Bottom triangle connection
    { x1: 50, y1: 155, x2: 110, y2: 155 },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 1, ease: 'easeOut' }}
      className="relative"
      style={{ width: '170px', height: '170px' }}
    >
      {/* Constellation lines */}
      <svg
        className="absolute inset-0 w-full h-full"
        style={{ overflow: 'visible' }}
      >
        {lines.map((line, i) => (
          <motion.line
            key={i}
            x1={line.x1}
            y1={line.y1}
            x2={line.x2}
            y2={line.y2}
            stroke="rgba(99, 102, 241, 0.4)"
            strokeWidth="1"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 1 }}
            transition={{ duration: 2, delay: i * 0.1, ease: 'easeInOut' }}
          />
        ))}
      </svg>

      {/* Stars */}
      {stars.map((star, i) => (
        <motion.div
          key={star.name}
          className="absolute"
          style={{
            left: `${star.x}px`,
            top: `${star.y}px`,
            width: `${star.size}px`,
            height: `${star.size}px`,
          }}
          initial={{ scale: 0, opacity: 0 }}
          animate={{ 
            scale: [1, 1.2, 1],
            opacity: [0.7, 1, 0.7]
          }}
          transition={{
            scale: {
              duration: 3,
              repeat: Infinity,
              delay: i * 0.3,
              ease: 'easeInOut'
            },
            opacity: {
              duration: 3,
              repeat: Infinity,
              delay: i * 0.3,
              ease: 'easeInOut'
            }
          }}
        >
          {/* Star glow */}
          <div
            className="absolute inset-0 rounded-full blur-md"
            style={{
              backgroundColor: star.glow,
              transform: 'translate(-50%, -50%)',
              width: `${star.size * 3}px`,
              height: `${star.size * 3}px`,
              left: '50%',
              top: '50%',
            }}
          />
          {/* Star core */}
          <div
            className="absolute inset-0 rounded-full"
            style={{
              backgroundColor: star.color,
              transform: 'translate(-50%, -50%)',
              left: '50%',
              top: '50%',
              boxShadow: `0 0 ${star.size * 2}px ${star.color}`,
            }}
          />
        </motion.div>
      ))}

      {/* Orion Nebula (M42) - glowing in the sword region */}
      <motion.div
        className="absolute"
        style={{
          left: '82px',
          top: '118px',
          width: '35px',
          height: '35px',
        }}
        initial={{ opacity: 0, scale: 0 }}
        animate={{ 
          opacity: [0.4, 0.6, 0.4],
          scale: [1, 1.15, 1],
        }}
        transition={{
          duration: 5,
          repeat: Infinity,
          delay: 1,
          ease: 'easeInOut'
        }}
      >
        <div
          className="absolute inset-0 rounded-full blur-2xl"
          style={{
            background: 'radial-gradient(circle, rgba(139,92,246,0.5) 0%, rgba(99,102,241,0.3) 35%, rgba(59,130,246,0.15) 70%, transparent 100%)',
          }}
        />
      </motion.div>
    </motion.div>
  );
}
