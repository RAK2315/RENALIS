import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const root=process.cwd(),skill='C:/Users/rehtr/.codex/plugins/cache/openai-primary-runtime/presentations/26.1015.12040/skills/presentations';
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')));
const manifest=JSON.parse(await fs.readFile('tmp/design-v06/manifest.json','utf8'));
for(const item of manifest){
 if(process.argv.includes('--architecture-only')&&item.key!=='architecture')continue;
 const folder=path.join(root,'tmp/design-v06',item.key),finalPath=path.join(root,'output/presentations',`${item.name}_${item.key==='architecture'?'Professional':'Design'}_Final.pptx`);
 const result=await finalizePresentation({materializeLiteralChartWorkbooks:true,requiredNativeChartOwnerSlides:item.chartOwners,workspaceDir:root,candidatePath:path.join(folder,'candidate.pptx'),finalPath,
 pythonExecutable:'C:/Users/rehtr/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','15240000,8572500','--validate-bullet-geometry','--validate-heading-fit'],fontPolicy:{basis:'design',families:['Segoe UI','Consolas']},verifyArtifactToolImport:true,receiptPath:path.join(folder,`validation-${path.basename(finalPath)}.json`)});
 console.log(item.key,JSON.stringify(result));
}
