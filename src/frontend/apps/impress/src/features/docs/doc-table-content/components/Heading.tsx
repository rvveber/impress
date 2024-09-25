import { BlockNoteEditor } from '@blocknote/core';
import { useState } from 'react';

import { BoxButton, Text } from '@/components';
import { useCunninghamTheme } from '@/cunningham';

const sizeMap: { [key: number]: string } = {
  1: '1.2rem',
  2: '1rem',
  3: '0.8rem',
};

export type HeadingsHighlight = {
  headingId: string;
  isVisible: boolean;
}[];

interface HeadingProps {
  editor: BlockNoteEditor;
  level: number;
  text: string;
  headingId: string;
  isHighlight: boolean;
}

export const Heading = ({
  headingId,
  editor,
  isHighlight,
  level,
  text,
}: HeadingProps) => {
  const [isHover, setIsHover] = useState(isHighlight);
  const { colorsTokens } = useCunninghamTheme();

  const color = isHighlight
    ? colorsTokens()['primary-600']
    : `${colorsTokens()['primary-600']}77`;

  return (
    <BoxButton
      key={headingId}
      onMouseOver={() => setIsHover(true)}
      onMouseLeave={() => setIsHover(false)}
      onClick={() => {
        editor.focus();
        editor.setTextCursorPosition(headingId, 'end');
        document.querySelector(`[data-id="${headingId}"]`)?.scrollIntoView({
          behavior: 'smooth',
          block: 'start',
        });
      }}
      $css="text-align: left;"
    >
      <Text
        $color={color}
        $padding={{ vertical: 'xtiny', left: 'tiny' }}
        $size={sizeMap[level]}
        $hasTransition
        $css={`
          ${isHover || isHighlight ? `box-shadow: -2px 0px 0px ${color};` : ''}
          overflow-wrap: anywhere;
        `}
        aria-selected={isHighlight}
        $weight={isHighlight ? 'bold' : 'normal'}
      >
        {text}
      </Text>
    </BoxButton>
  );
};
