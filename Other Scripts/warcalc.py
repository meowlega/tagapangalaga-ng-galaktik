// The DEFINITIVE FINAL code for galaktikv1/index.ts
import { serve } from 'https://deno.land/std@0.177.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';
// --- CONFIGURATION ---
const FB_VERIFY_TOKEN = Deno.env.get('FB_VERIFY_TOKEN');
const FB_PAGE_ACCESS_TOKEN = Deno.env.get('FB_PAGE_ACCESS_TOKEN');
// --- LOGIC AND HELPERS ---
const ROLES = {
  0: 'Gen',
  1: 'Capt',
  2: 'Priv'
};
const HQ_LEVEL_TO_WAR_POINTS = {
  1: 100,
  2: 200,
  3: 300,
  4: 400,
  5: 600,
  6: 1000,
  7: 1500,
  8: 2000,
  9: 2500
};
function padNumber(num, length) {
  return String(num).padStart(length, ' ');
}
function formatNumberWithSpaces(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}
function calculateTotalWarPoints(members, usersDataMap) {
  let totalPoints = 0;
  for (const member of members){
    const userData = usersDataMap.get(member.Id);
    if (!userData || userData.error) {
      continue;
    }
    const planets = userData.Planets || [];
    for (const planet of planets){
      const hqLevel = planet.HQLevel || 0;
      totalPoints += HQ_LEVEL_TO_WAR_POINTS[hqLevel] || 0;
    }
  }
  return totalPoints;
}
function calculateWarStats(allyMembers, enemyMembers, usersDataMap) {
  const totalWpAlly = calculateTotalWarPoints(allyMembers, usersDataMap);
  const totalWpEnemy = calculateTotalWarPoints(enemyMembers, usersDataMap);
  if (totalWpAlly === 0 || totalWpEnemy === 0) {
    return {
      message: "Cannot perform calculation...",
      totalWpAlly,
      totalWpEnemy
    };
  }
  const caseAlly = Math.floor(totalWpAlly / 2540) + 1;
  const caseEnemy = Math.floor(totalWpEnemy / 2540) + 1;
  if (caseAlly === 0) {
    return {
      message: "Cannot calculate...",
      totalWpAlly,
      totalWpEnemy,
      caseAlly,
      caseEnemy
    };
  }
  const regenTime = Math.floor(3 + Math.abs(caseEnemy - caseAlly) * 3 / caseAlly);
  let regenHoursAlly;
  let regenHoursEnemy;
  if (caseAlly >= caseEnemy) {
    regenHoursAlly = regenTime;
    regenHoursEnemy = 3;
  } else {
    regenHoursAlly = 3;
    regenHoursEnemy = regenTime;
  }
  return {
    totalWpAlly,
    totalWpEnemy,
    caseAlly,
    caseEnemy,
    regenerationHours: {
      ally: regenHoursAlly,
      enemy: regenHoursEnemy
    }
  };
}
function formatSimpleStatus(data) {
  // CHANGED: Use `data.Id` instead of `data.allyName`
  let message = `Alliance Found: ${data.Id}\n\n`;
  message += `Status: Not currently in a war.\n`;
  // CHANGED: Use `data.WarPoints` instead of `data.allyWarPoints`
  message += `Current War Points: ${formatNumberWithSpaces(data.WarPoints)}\n\n`;
  message += `Type another alliance name to search again.`;
  return message;
}
function formatWarReport(data, sortedMembers) {
  const calculations = data.warCalculations;
  let message = `⚔️ War Report: ${data.allyName} ⚔️\n\n`;
  message += `Opponent: ${data.OpponentName}\n\n`;
  if (calculations && calculations.regenerationHours) {
    message += `--- Regeneration Time ---\n`;
    message += `${data.allyName}: ${calculations.regenerationHours.ally} hours\n`;
    message += `${data.OpponentName}: ${calculations.regenerationHours.enemy} hours\n`;
  }
  message += `\n--- Enemy Colony Intel ---\n`; // Renamed for clarity
  sortedMembers.forEach((member)=>{
    const roleText = ROLES[member.AllianceRole] || 'Unknown';
    message += `\n${member.Name} (${member.Id}) 🗡 ${roleText} ✪ ${member.Level}\n`;
    message += `✨ ${formatNumberWithSpaces(member.TotalWarPoints)}\n`;
    if (member.planetDetails && member.planetDetails.length > 0) {
      // --- FINAL, SIMPLIFIED LOGIC ---
      // Only show discovered colonies (planetId > 1)
      member.planetDetails.forEach((planet)=>{
        if (planet.planetId > 1 && planet.status === 'Discovered') {
          const displayPId = padNumber(planet.planetId - 1, 2); // 1-indexed colony ID
          const hq = planet.hqLevel;
          const x = padNumber(planet.coordinates.x, 4);
          const y = padNumber(planet.coordinates.y, 4);
          message += `  🪐 ${displayPId} ${x} ${y} 🏠 ${hq}\n`;
        }
      });
    }
  });
  return message;
}
async function sendTextMessage(recipientId, text) {
  const MAX_LENGTH = 2000;
  const chunks = [];
  for(let i = 0; i < text.length; i += MAX_LENGTH){
    chunks.push(text.substring(i, i + MAX_LENGTH));
  }
  for (const chunk of chunks){
    const messageData = {
      recipient: {
        id: recipientId
      },
      message: {
        text: chunk
      }
    };
    try {
      const fbResponse = await fetch(`https://graph.facebook.com/v18.0/me/messages?access_token=${FB_PAGE_ACCESS_TOKEN}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(messageData)
      });
      if (!fbResponse.ok) {
        const errorData = await fbResponse.json();
        console.error("Facebook API Error:", errorData.error.message);
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  }
}
// --- MAIN SERVER LOGIC ---
serve(async (req)=>{
  if (req.method === 'GET' && new URL(req.url).searchParams.get('hub.mode') === 'subscribe') {
    const url = new URL(req.url);
    const hubChallenge = url.searchParams.get('hub.challenge');
    const hubVerifyToken = url.searchParams.get('hub.verify_token');
    if (hubVerifyToken === FB_VERIFY_TOKEN) {
      console.log("Webhook verified!");
      return new Response(hubChallenge, {
        status: 200
      });
    } else {
      console.error("Webhook verification failed.");
      return new Response('Verification token mismatch', {
        status: 403
      });
    }
  }
  if (req.method === 'POST') {
    const payload = await req.json();
    if (payload.object !== 'page') return new Response('Not a page event', {
      status: 200
    });
    for (const entry of payload.entry){
      for (const event of entry.messaging){
        if (event.message && !event.message.is_echo) {
          const senderId = event.sender.id;
          const messageText = event.message.text?.trim() || '';
          if (!messageText) continue;
          await sendTextMessage(senderId, `Searching for "${messageText}"...`);
          try {
            const supabase = createClient(Deno.env.get('SUPABASE_URL'), Deno.env.get('SUPABASE_ANON_KEY'));
            const fetchOptions = {
              headers: {
                'User-Agent': 'Mozilla/5.0'
              },
              cache: 'no-cache'
            };
            const primaryAllianceResponse = await fetch(`https://api.galaxylifegame.net/Alliances/get?name=${encodeURIComponent(messageText)}`, fetchOptions);
            if (!primaryAllianceResponse.ok) {
              if (primaryAllianceResponse.status === 404) {
                await sendTextMessage(senderId, `Sorry, I couldn't find an alliance named "${messageText}". Please check the spelling.`);
              } else {
                throw new Error(`Game API Error: ${primaryAllianceResponse.status}`);
              }
              continue;
            }
            let primaryAllianceData;
            try {
              primaryAllianceData = await primaryAllianceResponse.json();
            } catch (jsonError) {
              await sendTextMessage(senderId, `Sorry, "${messageText}" doesn't seem to be a valid alliance name.`);
              continue;
            }
            if (!primaryAllianceData.InWar) {
              await sendTextMessage(senderId, formatSimpleStatus(primaryAllianceData));
              continue;
            }
            const opponentAllianceResponse = await fetch(`https://api.galaxylifegame.net/Alliances/get?name=${encodeURIComponent(primaryAllianceData.OpponentAllianceId)}`, fetchOptions);
            const opponentAllianceData = opponentAllianceResponse.ok ? await opponentAllianceResponse.json() : null;
            if (!opponentAllianceData) {
              throw new Error("Could not fetch opponent data.");
            }
            const memberIdsToFetch = new Set();
            primaryAllianceData.Members.forEach((m)=>memberIdsToFetch.add(m.Id));
            opponentAllianceData.Members.forEach((m)=>memberIdsToFetch.add(m.Id));
            const userFetchPromises = Array.from(memberIdsToFetch).map(async (id)=>{
              const res = await fetch(`https://api.galaxylifegame.net/Users/get?id=${id}`, fetchOptions);
              if (res.ok) return res.json();
              return {
                Id: id,
                error: `Failed to fetch user: ${res.status}`
              };
            });
            const allUsersDataResults = await Promise.all(userFetchPromises);
            const usersDataMap = new Map(allUsersDataResults.map((u)=>[
                u.Id,
                u
              ]));
            const enrichedEnemyMembers = await Promise.all(opponentAllianceData.Members.map(async (member)=>{
              const baseInfo = usersDataMap.get(member.Id);
              let planetDetails = [];
              if (baseInfo && baseInfo.Planets) {
                planetDetails = await Promise.all(baseInfo.Planets.map(async (planet, index)=>{
                  const planetId = index + 1;
                  const hqLevel = planet.HQLevel;
                  const { data } = await supabase.from('planets').select('coordX, coordY').eq('accountId', member.Id).eq('planetId', planetId).single();
                  return data ? {
                    planetId,
                    hqLevel,
                    status: "Discovered",
                    coordinates: {
                      x: data.coordX,
                      y: data.coordY
                    }
                  } : {
                    planetId,
                    hqLevel,
                    status: "Not yet discovered",
                    coordinates: null
                  };
                }));
              }
              return {
                ...member,
                baseInfo,
                planetDetails
              };
            }));
            const warCalculations = calculateWarStats(primaryAllianceData.Members, opponentAllianceData.Members, usersDataMap);
            const sortedMembers = enrichedEnemyMembers.sort((a, b)=>{
              const roleA = a.AllianceRole ?? 99;
              const roleB = b.AllianceRole ?? 99;
              if (roleA !== roleB) return roleA - roleB;
              return (b.TotalWarPoints ?? 0) - (a.TotalWarPoints ?? 0);
            });
            const finalData = {
              allyName: primaryAllianceData.Id,
              OpponentName: primaryAllianceData.OpponentAllianceId,
              warCalculations
            };
            await sendTextMessage(senderId, formatWarReport(finalData, sortedMembers));
          } catch (error) {
            console.error('Bot processing error:', error);
            await sendTextMessage(senderId, `An unexpected error occurred. Please try again.`);
          }
        }
      }
    }
    return new Response('EVENT_RECEIVED', {
      status: 200
    });
  }
  return new Response('Not Found', {
    status: 404
  });
});