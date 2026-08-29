/** Labeled contest fallback when Sarvam inference returns 402. */

export const DEMO_BANNER =
  "Sarvam inference credits are empty, so Vaani is using a labeled on-page demo. Shared WebMCP state still updates. Add credits at dashboard.sarvam.ai/billing for live STT/TTS/LLM/translate.";

const MR_TRANSLATE =
  "एजेंटिक वेबने सर्वांनी इंग्रजी टाईप करणे अपेक्षित मानू नये. माणसांनी आपल्या भाषेत बोलावे. ब्राउझर एजंटांनी त्याच पृष्ठावरील संरचित साधने वापरावीत जी माणूस पाहतो.";

const HI_TRANSLATE =
  "एजेंटिक वेब यह न माने कि हर कोई अंग्रेज़ी टाइप करता है। इंसान अपनी भाषा में बोलें। ब्राउज़र एजेंट उसी पेज पर संरचित टूल चलाएँ जो इंसान देखता है।";

export function demoTranslate(target: string): string {
  if (target.startsWith("hi")) return HI_TRANSLATE;
  if (target.startsWith("en")) {
    return "The agentic web should not assume everyone types English. Humans should speak in their language. Browser agents should call structured tools on the same page the human sees.";
  }
  return MR_TRANSLATE;
}

export function demoExplain(target: string): string {
  if (target.startsWith("hi")) {
    return "यह पाठ कहता है कि एजेंटिक वेब बहुभाषी होना चाहिए: इंसान बोलें, एजेंट वही स्क्रीन अपडेट करें।";
  }
  if (target.startsWith("en")) {
    return "This passage argues the agentic web must be multilingual: humans speak natively while agents update the same visible workspace.";
  }
  return "हा उतारा सांगतो की एजेंटिक वेब बहुभाषिक असावे: माणूस बोलतो, एजेंट तीच स्क्रीन बदलतो.";
}

export function demoSummary(target: string): string {
  if (target.startsWith("hi")) {
    return "1) अंग्रेज़ी गेट हटाएँ। 2) आवाज़ + भाषा। 3) इंसान और एजेंट एक ही ऐप स्थिति साझा करें।";
  }
  if (target.startsWith("en")) {
    return "1) Drop the English gate. 2) Voice plus language. 3) Humans and agents share one app state.";
  }
  return "1) इंग्रजी गेट काढा. 2) आवाज आणि भाषा. 3) माणूस आणि एजंट एकच अॅप स्थिती वापरावी.";
}

export function demoTranscript(): { transcript: string; language: string } {
  return {
    transcript: "हा document समजावून सांग आणि तीन महत्त्वाचे मुद्दे काढ.",
    language: "mr-IN",
  };
}
