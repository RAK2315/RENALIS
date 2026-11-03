// Plain-English names shown in the UI. The backend keeps its technical labels;
// the frontend maps them by id so non-specialists can follow every screen.

export const familyName: Record<string, string> = {
  volume: 'Not enough blood volume',
  vascular: 'Blood vessels not tightening',
  cardiac: 'Heart not pumping harder',
  mixed: 'A mix of causes',
};

export const familyShort: Record<string, string> = {
  volume: 'Blood volume',
  vascular: 'Blood vessels',
  cardiac: 'Heart',
  mixed: 'Mix',
};

export const familyExplain: Record<string, string> = {
  volume: 'The machine removes water faster than the body can move water back into the blood, so blood volume runs low.',
  vascular: 'Blood volume is fine, but the blood vessels do not squeeze tighter to hold pressure up the way they normally would.',
  cardiac: 'The heart does not speed up or pump harder to make up for the water being removed.',
  mixed: 'A bit of each. Real patients often have more than one cause at once.',
};

export const channelName: Record<string, string> = {
  repeat_bp: 'Re-check blood pressure',
  relative_blood_volume: 'Blood volume sensor',
  cardiac_output: 'Heart pumping measurement',
};

export const channelExplain: Record<string, string> = {
  repeat_bp: 'A normal arm-cuff reading. Cheap and always available.',
  relative_blood_volume: 'A sensor on the dialysis machine that tracks how much blood volume has dropped since the start.',
  cardiac_output: 'How many litres of blood the heart pumps per minute. Needs extra equipment.',
};

export const plainLabel = (id: string, fallback: string) => familyName[id] ?? channelName[id] ?? fallback;
