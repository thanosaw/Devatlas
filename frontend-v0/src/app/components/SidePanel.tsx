import React from 'react';
import Image from 'next/image';

interface SidePanelProps {
  topIcons: React.ReactNode[];
  bottomIcon: string; // Path to the bottom image
}

const SidePanel: React.FC<SidePanelProps> = ({ topIcons, bottomIcon }) => {
  return (
    <div className="fixed left-0 top-0 w-[70px] z-[30] h-screen flex flex-col items-center" 
         style={{ 
           background: '#EFEFEF',
           borderRight: '1px solid rgba(0, 0, 0, 0.50)'
         }}>
      {/* Top icons section */}
      <div className="mt-[26px] flex flex-col items-center gap-[32px]">
        {topIcons.map((icon, index) => (
          <div key={index} className="w-[32px] h-[32px] flex items-center justify-center">
            {icon}
          </div>
        ))}
      </div>
      
      {/* Bottom icon */}
      <div className="absolute bottom-[26px] w-[32px] h-[32px]">
        <Image 
          src={bottomIcon}
          alt="Bottom Icon"
          width={32}
          height={32}
        />
      </div>
    </div>
  );
};

export default SidePanel; 