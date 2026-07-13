# 6학년 영어 복습 부루마블 웹앱 — 구현 스펙

## 목표
천재(함순애) 6학년 영어 1~6단원 복습용 부루마블형 보드게임. 기본은 1인 1태블릿 개인전(학생 1명 + 봇 3명), 보조로 모둠 핫시트 모드 지원. 순수 HTML/CSS/JS 단일 파일, API·서버·외부 라이브러리 없음(예외: Jua 폰트 1건, 개인전 점수 제출용 Google Form POST).

## 기술 제약
- 단일 `index.html` (인라인 CSS/JS). 외부 요청 없음.
- 태블릿 터치 최적화: 버튼 최소 48px, 모든 입력은 터치(타이핑 없음).
- localStorage 자동 저장. 페이지 로드 시 저장된 게임이 있으면 "이어하기 / 새 게임" 선택.
- 배포: `nuno4623.github.io/lessons/6영어/board-game/index.html` (GitHub Pages).
- 데이터·엔진 완전 분리: 파일 최상단 `SUBJECTS` 객체만 교체하면 4학년/타 과목 확장 가능. 시작 화면에 과목 선택 UI 포함(현재는 eng6 하나).

## 화면 구성
1. **시작 화면**: 과목 선택(드롭다운, 현재 "6학년 영어"만) → 플레이 모드 선택:
   - **개인전 (기본)**: 반/번호 입력 → `번호 % 4`로 팀 자동 배정(팀 이름·색 크게 표시: 1팀 빨강 / 2팀 파랑 / 3팀 노랑 / 4팀 초록) → 봇 난이도(쉬움 50% / 보통 60% / 어려움 70% 정답률) → 게임 시간(10/15/20분) → 시작. 학생 1명 + 봇 3명 플레이.
   - **모둠전 (핫시트)**: 팀 수(2/3/4) → 팀 이름 입력(기본값: 1모둠~4모둠) → 게임 시간(15/20/25분) → 시작. 모둠당 태블릿 1대로 돌아가며 플레이.
2. **게임 화면**: 중앙 7×7 보드(둘레 24칸), 보드 중앙에 주사위 버튼·현재 팀·타이머. 하단(또는 측면)에 팀 패널(이름/점수/획득 땅 수, 현재 턴 강조). 개인전에서는 봇 턴이 자동 진행(주사위 애니메이션 포함, 턴당 2초 내외로 빠르게).
3. **문제 모달**: 칸 도착 시 표시. 정답/오답 피드백 후 정답 문장 노출(2초). 개인전에서 봇은 문제 없이 설정된 정답률로 즉시 판정.
4. **결과 화면**: 타이머 종료 시 점수 순위 + 팀별 획득 땅 표시, "다시 하기" 버튼. **개인전은 결과 화면에 "점수 제출" 버튼 추가** → 아래 점수 집계 방식 참조.

## 개인전 점수 집계 (서버 없이 팀 대항)
- 반 전체가 동시에 각자 태블릿으로 플레이(같은 제한시간) → 종료 후 점수를 Google Form으로 자동 제출 → 연결된 시트에서 팀별 합산.
- 구현: 제출 버튼 클릭 시 Google Form 응답 URL로 `fetch` POST (`mode: "no-cors"`, entry ID 매핑: 반/번호/배정팀/점수/획득 땅 수). API 키 불필요.
- Form URL과 entry ID는 코드 상단 상수로 분리 (`SUBMIT_FORM` 객체). 값이 비어 있으면 제출 버튼 숨김 처리 — Form은 배포 후 별도 생성해 값만 채워 넣는 방식.
- 제출 성공 여부는 no-cors 특성상 확인 불가하므로, 제출 후 "제출 완료! 선생님 화면을 확인하세요" 안내 + 중복 제출 방지(localStorage 플래그).

## 보드 배치 (24칸, 시계 반대 방향 이동, index 0 = 출발)
7×7 그리드 둘레. 그리드 좌표 매핑:
- 아래줄 (row 6): col 6→0 = index 0~6
- 왼쪽줄 (col 0): row 5→1 = index 7~11
- 윗줄 (row 0): col 0→6 = index 12~18
- 오른쪽줄 (col 6): row 1→5 = index 19~23

| index | 칸 |
|---|---|
| 0 | 출발 (모서리) |
| 1~3 | 1단원 |
| 4 | 황금열쇠 |
| 5 | 2단원 |
| 6 | 무인도 (모서리) |
| 7~8 | 2단원 |
| 9~11 | 3단원 |
| 12 | 세계여행 (모서리) |
| 13~15 | 4단원 |
| 16 | 황금열쇠 |
| 17 | 5단원 |
| 18 | 더블찬스 (모서리) |
| 19~20 | 5단원 |
| 21~23 | 6단원 |

칸에는 단원명이 아니라 **각 단원의 `cities` 배열에 정의된 도시(국기 이모지 + 도시명 + 가치)**를 순서대로 표시한다. 단원↔칸 매핑은 내부 로직 전용.

단원 색 (칸 배경, 파스텔 톤 유지): 1단원 보라 #7c4dff · 2단원 청록 #00bfa5 · 3단원 코랄 #ff7043 · 4단원 핑크 #ec407a · 5단원 파랑 #42a5f5 · 6단원 앰버 #ffb300. 특수칸 회색 계열. 팀 말은 색 점 4종(빨/파/노/초)으로 칸 안에 표시.

## 게임 규칙
- 주사위 1개(1~6), 굴리기 애니메이션(숫자 롤링 0.8초 정도).
- **도시 칸(주인 없음)**: 그 칸에 매핑된 단원의 문제 1개 출제 → 정답: 도시 획득 + 도시 가치만큼 점수 / 오답: 아무 일 없음.
- **도시 칸(자기 땅)**: 자동 +30점 (문제 없음).
- **도시 칸(남의 땅)**: 통행료 문제 출제 → 정답: 면제 / 오답: 자기 팀 -도시 가치의 절반, 땅 주인 +도시 가치의 절반.
- **도시 가치**: 구역별 차등 (출발에서 멀수록 비쌈): 1구역 80 / 2구역 90 / 3구역 100 / 4구역 110 / 5구역 120 / 6구역 130. 칸에 가치 표시.
- **출발**: 지나갈 때마다 +50점.
- **황금열쇠**: 카드 랜덤 1장. 카드 풀: [+80점 보너스 / -40점 벌금 / 앞으로 2칸 / 뒤로 2칸 / 출발로 이동(+50 포함) / 한 번 더 굴리기 / 다음 문제 점수 2배 / 무인도로 이동]. 이동 카드는 도착 칸 이벤트도 처리.
- **무인도**: 다음 자기 턴 1회 쉬기.
- **세계여행**: 보드의 원하는 칸을 터치해 이동(이동 후 도착 칸 이벤트 처리).
- **더블찬스**: 그 팀의 다음 문제 획득/손실 점수 2배.
- 문제는 단원별 문제은행에서 비복원 랜덤 추출, 소진 시 리셋 후 재사용.
- 타이머 종료 시 즉시 결과 화면. 점수 동점이면 획득 땅 수로 판정.

## 문제 유형 (3종, 전부 터치 조작)
- `c` 4지선다: 질문 + 보기 4개 버튼.
- `b` 빈칸: 문장 속 `___` + 보기 4개 버튼 (UI는 4지선다와 동일하되 빈칸 강조 스타일).
- `o` 문장 배열: 한글 해석 제시 + 단어 칩(섞어서 표시)을 터치해 순서대로 배치. 배치한 칩 다시 터치하면 되돌리기. **`x` 배열의 함정 단어가 칩에 섞여 표시됨** — 함정 단어를 쓰지 않고 `w` 순서대로 완성해야 정답. "확인" 버튼은 `w` 개수만큼 배치하면 활성화.

## 데이터 스키마 + 문제은행 (아래 그대로 사용)
```js
const SUBJECTS = {
  eng6: {
    name: "6학년 영어 (1~6단원)",
    units: [
      { id: 1, color: "#7c4dff", value: 80,
        cities: [{n:"서울",f:"🇰🇷"},{n:"도쿄",f:"🇯🇵"},{n:"베이징",f:"🇨🇳"}],
        questions: [
        { t:"c", q:"A: How do you spell your name?
B: ___", o:["J-I-N-H-O.","I'm Jinho.","I'm in the fifth grade.","Nice to meet you."], a:0 },
        { t:"c", q:"어법상 틀린 문장은?", o:["I'm in the six grade.","I'm in the sixth grade.","What grade are you in?","I play the guitar every day."], a:0 },
        { t:"b", q:"I ___ the guitar every day.", o:["play","plays","playing","played"], a:0 },
        { t:"c", q:"A: What grade are you in?
B: ___
A: Oh! We're in the same grade!", o:["I'm in the sixth grade.","I'm eleven years old.","I like my school.","How about you?"], a:0 },
        { t:"b", q:"A: How do you ___ your name?
B: K-I-M.", o:["spell","call","say","write"], a:0 },
        { t:"c", q:"'first, second, third' 다음에 이어질 두 개는?", o:["fourth - fifth","four - five","fourth - fiveth","forth - fifth"], a:0 },
        { t:"c", q:"'나는 매일 드럼을 쳐.'를 바르게 쓴 것은?", o:["I play the drum every day.","I plays the drum every day.","I play the drum every days.","I am play the drum every day."], a:0 },
        { t:"b", q:"Good ___ with your show! (행운을 빌어)", o:["luck","lucky","luckily","like"], a:0 },
        { t:"c", q:"'What grade are you in?'의 대답으로 어색한 것은?", o:["I'm eleven years old.","I'm in the sixth grade.","I'm in the fifth grade.","I'm in the third grade."], a:0 },
        { t:"o", ko:"나는 6학년이야.", w:["I'm","in","the","sixth","grade."], x:["six"] },
        { t:"o", ko:"너는 이름 철자가 어떻게 되니?", w:["How","do","you","spell","your","name?"], x:["what"] },
        { t:"o", ko:"나는 매일 기타를 연주해.", w:["I","play","the","guitar","every","day."], x:["plays"] }
      ]},
      { id: 2, color: "#00bfa5", value: 90,
        cities: [{n:"방콕",f:"🇹🇭"},{n:"싱가포르",f:"🇸🇬"},{n:"시드니",f:"🇦🇺"}],
        questions: [
        { t:"c", q:"A: What season do you like?
B: I like winter. ___", o:["I can ski with my family.","I can see beautiful flowers.","It's very hot.","I don't like snow."], a:0 },
        { t:"c", q:"내용이 어색한 문장은?", o:["I like spring. It's cold and snowy.","I like summer. I can swim.","I like fall. The sky is clear.","I like winter. I can ski."], a:0 },
        { t:"b", q:"I can see beautiful flowers ___ spring.", o:["in","on","at","to"], a:0 },
        { t:"b", q:"A: Look! I made this card.
B: ___!", o:["Good job","Good luck","I can't wait","Don't worry"], a:0 },
        { t:"c", q:"'들판이 밝고 강물이 맑다'에 쓸 단어 짝은?", o:["bright - clear","cold - warm","little - also","trip - card"], a:0 },
        { t:"c", q:"시에서 'The sky is high and clear.'가 어울리는 계절은?", o:["fall","spring","summer","winter"], a:0 },
        { t:"b", q:"What season ___ you like?", o:["do","does","are","is"], a:0 },
        { t:"c", q:"'We went on a trip to the river.'에서 trip의 뜻은?", o:["여행","선물","카드","계절"], a:0 },
        { t:"c", q:"'What season do you like?'의 대답으로 어색한 것은?", o:["I like rainy days.","I like spring.","I like fall.","I like winter."], a:0 },
        { t:"o", ko:"너는 무슨 계절을 좋아하니?", w:["What","season","do","you","like?"], x:["is"] },
        { t:"o", ko:"나는 봄에 아름다운 꽃을 볼 수 있어.", w:["I","can","see","beautiful","flowers","in","spring."], x:["am"] },
        { t:"o", ko:"하늘이 맑아.", w:["The","sky","is","clear."], x:["clean"] }
      ]},
      { id: 3, color: "#ff7043", value: 100,
        cities: [{n:"카이로",f:"🇪🇬"},{n:"이스탄불",f:"🇹🇷"},{n:"두바이",f:"🇦🇪"}],
        questions: [
        { t:"c", q:"'It's on March 22nd.'가 뜻하는 날짜는?", o:["3월 22일","3월 12일","5월 22일","3월 2일"], a:0 },
        { t:"b", q:"My birthday is ___ July 31st.", o:["on","in","at","of"], a:0 },
        { t:"c", q:"서수 표기가 틀린 것은?", o:["twenty-oneth","ninth","twenty-second","thirty-first"], a:0 },
        { t:"c", q:"A: The school market is on May 9th.
B: ___", o:["I can't wait!","Good job!","Don't worry.","That's not right."], a:0 },
        { t:"b", q:"We can ___ paper. (종이를 아낄 수 있어)", o:["save","turn","off","buy"], a:0 },
        { t:"c", q:"Earth Day 포스터 문구로 알맞은 것은?", o:["Save the earth!","Break the earth!","Buy the earth!","Wear the earth!"], a:0 },
        { t:"c", q:"'It's on November 6th.'의 질문으로 알맞은 것은?", o:["When is the school trip?","Where is the school trip?","Why do you like the trip?","What is the trip?"], a:0 },
        { t:"b", q:"Turn ___ the water. (물을 잠가)", o:["off","on","up","in"], a:0 },
        { t:"c", q:"'5월 23일'을 영어로 바르게 읽은 것은?", o:["May twenty-third","May twenty-three","May two-three","March twenty-third"], a:0 },
        { t:"o", ko:"네 생일은 언제니?", w:["When","is","your","birthday?"], x:["What"] },
        { t:"o", ko:"내 생일은 5월 7일이야.", w:["My","birthday","is","on","May","7th."], x:["at"] },
        { t:"o", ko:"우리는 지구를 구할 수 있어.", w:["We","can","save","the","earth."], x:["saves"] }
      ]},
      { id: 4, color: "#ec407a", value: 110,
        cities: [{n:"파리",f:"🇫🇷"},{n:"런던",f:"🇬🇧"},{n:"로마",f:"🇮🇹"}],
        questions: [
        { t:"c", q:"A: Why are you sad?
B: ___", o:["Because I can't find my bike.","Because I got a black belt.","Good job!","Yes, I am."], a:0 },
        { t:"b", q:"A: Oh no, I broke my mom's cup.
B: ___ I'll help you.", o:["Don't worry.","I can't wait!","Good luck!","Congratulations!"], a:0 },
        { t:"c", q:"어법상 틀린 문장은?", o:["Why you are happy?","Why are you sad?","Why are you angry?","Why are you happy?"], a:0 },
        { t:"b", q:"Because I ___ my leg. (다리가 부러졌어)", o:["broke","break","breaks","broken"], a:0 },
        { t:"c", q:"'Congratulations!'를 쓰기에 알맞은 상황은?", o:["친구가 퀴즈 대회에서 우승했을 때","친구가 자전거를 잃어버렸을 때","친구가 시험을 망쳤을 때","친구가 길을 물어볼 때"], a:0 },
        { t:"c", q:"A: Why are you happy?
B: Because I passed the test.
A: ___", o:["Congratulations!","Don't worry.","I'm sorry.","Because I'm happy."], a:0 },
        { t:"b", q:"___ are you worried? - Because I have a test today.", o:["Why","When","What","Where"], a:0 },
        { t:"c", q:"'Something is ___ with my computer.' (뭔가 잘못됐어)", o:["wrong","worry","because","break"], a:0 },
        { t:"c", q:"'I made a birdhouse.'에서 birdhouse의 뜻은?", o:["새집","새장","새 모이","나무 집"], a:0 },
        { t:"o", ko:"너는 왜 걱정하니?", w:["Why","are","you","worried?"], x:["do"] },
        { t:"o", ko:"검은 띠를 땄기 때문이야.", w:["Because","I","got","a","black","belt."], x:["get"] },
        { t:"o", ko:"걱정하지 마. 내가 도와줄게.", w:["Don't","worry.","I'll","help","you."], x:["not"] }
      ]},
      { id: 5, color: "#42a5f5", value: 120,
        cities: [{n:"베를린",f:"🇩🇪"},{n:"마드리드",f:"🇪🇸"},{n:"암스테르담",f:"🇳🇱"}],
        questions: [
        { t:"c", q:"'Go straight two blocks and turn left. It's next to the hospital.'와 일치하는 설명은?", o:["두 블록 직진 후 왼쪽, 병원 옆","한 블록 직진 후 왼쪽, 병원 옆","두 블록 직진 후 오른쪽, 병원 옆","두 블록 직진 후 왼쪽, 병원 건너편"], a:0 },
        { t:"b", q:"Go straight one ___ and turn right.", o:["block","street","stop","town"], a:0 },
        { t:"c", q:"어법상 틀린 문장은?", o:["Turn to right at the bank.","Turn right at the bank.","Go straight one block.","It's next to the store."], a:0 },
        { t:"b", q:"There ___ a small park in Hanok Town.", o:["is","are","be","am"], a:0 },
        { t:"c", q:"A: Where is the restroom?
B: ___", o:["Go straight and turn left at the store.","I like the restroom.","Because I'm hungry.","It's ten o'clock."], a:0 },
        { t:"c", q:"'It's next to the bank.'의 뜻은?", o:["은행 옆에 있다","은행 앞에 있다","은행 뒤에 있다","은행 안에 있다"], a:0 },
        { t:"b", q:"I'm ___. Where is a restaurant? (배가 고파)", o:["hungry","angry","happy","sleepy"], a:0 },
        { t:"c", q:"장소와 설명이 잘못 연결된 것은?", o:["restroom - 밥을 먹는 곳","hospital - 아픈 사람을 치료하는 곳","bank - 돈을 맡기는 곳","restaurant - 음식을 파는 곳"], a:0 },
        { t:"c", q:"'There is a small park in Hanok Town.'의 뜻은?", o:["한옥마을에 작은 공원이 있다","한옥마을은 작은 공원이다","작은 공원에 한옥마을이 있다","한옥마을에 큰 공원이 있다"], a:0 },
        { t:"o", ko:"누리 은행에서 오른쪽으로 도세요.", w:["Turn","right","at","Nuri","Bank."], x:["left"] },
        { t:"o", ko:"두 블록 곧장 가세요.", w:["Go","straight","two","blocks."], x:["block"] },
        { t:"o", ko:"그것은 도서관 옆에 있어요.", w:["It's","next","to","the","library."], x:["at"] }
      ]},
      { id: 6, color: "#ffb300", value: 130,
        cities: [{n:"뉴욕",f:"🇺🇸"},{n:"토론토",f:"🇨🇦"},{n:"리우",f:"🇧🇷"}],
        questions: [
        { t:"c", q:"A: What does your aunt look like?
B: ___", o:["She has long brown hair.","She is a teacher.","She likes music.","She is at home."], a:0 },
        { t:"b", q:"She ___ blue eyes and short gray hair.", o:["has","have","is","does"], a:0 },
        { t:"c", q:"어법상 틀린 문장은?", o:["He is wear a blue shirt.","He is wearing a blue shirt.","She is wearing red glasses.","He has short hair."], a:0 },
        { t:"b", q:"He and I look the ___. (우리는 똑같이 생겼어)", o:["same","short","long","like"], a:0 },
        { t:"c", q:"'She has long hair. She is wearing a yellow dress.'에 맞는 사람은?", o:["긴 머리에 노란 원피스","짧은 머리에 노란 원피스","긴 머리에 노란 셔츠","긴 머리에 파란 원피스"], a:0 },
        { t:"c", q:"'my aunt's daughter'는 나에게 누구?", o:["사촌","이모","딸","언니"], a:0 },
        { t:"b", q:"What ___ she look like?", o:["does","is","do","has"], a:0 },
        { t:"c", q:"옷차림을 묘사하는 문장은?", o:["She is wearing a white dress.","She has big eyes.","She has long hair.","She is my aunt."], a:0 },
        { t:"c", q:"'We are in the same club.'에서 same의 뜻은?", o:["같은","비슷한","다른","특별한"], a:0 },
        { t:"o", ko:"그는 어떻게 생겼니?", w:["What","does","he","look","like?"], x:["is"] },
        { t:"o", ko:"그녀는 파란 눈과 짧은 머리를 가졌어.", w:["She","has","blue","eyes","and","short","hair."], x:["is"] },
        { t:"o", ko:"그는 노란 셔츠와 파란 바지를 입고 있어.", w:["He","is","wearing","a","yellow","shirt","and","blue","pants."], x:["has"] }
      ]}
    ]
  }
  // eng4: 4학년 확장 시 동일 구조로 블록 추가
};
```

**구현 주의**:
- `c`/`b` 유형은 정답이 전부 index 0이므로, 렌더링 시 보기 순서를 반드시 셔플하고 정답 index를 재계산할 것.
- `o` 유형은 `w`(정답 순서) + `x`(함정 단어)를 합쳐 셔플해 칩으로 표시. 함정 단어를 쓰지 않고 `w` 순서 그대로 배치해야 정답. 셔플 결과가 정답 순서와 같으면 재셔플.
- `q`의 `\n`은 대화문 줄바꿈 — 모달에서 줄바꿈으로 렌더링할 것.
- 문항 난이도는 중상 수준(어법 판단·대화 완성·함정 보기 포함)으로 작성됨. 셀 표시용 도시 데이터(`cities`)와 문제 출제용 단원은 내부에서만 연결되고 학생에게 단원 정보는 노출하지 않음.

## 폴더/배포
- 경로: `nuno4623.github.io/lessons/6영어/board-game/index.html`
- 커밋 후 GitHub Pages URL 확인, QR 생성은 별도 요청 시.

## 완료 체크리스트
- [ ] 태블릿(가로/세로) 양방향 레이아웃 확인
- [ ] 보기 셔플 동작 확인 (같은 문제 두 번 출제 시 순서 다름)
- [ ] localStorage 이어하기: 새로고침 후 상태 복원
- [ ] 세계여행 칸 터치 이동 + 도착 이벤트 연쇄 처리
- [ ] 타이머 종료 시 진행 중 문제 모달은 마저 처리 후 결과 화면
- [ ] 더블찬스 2배가 통행료 손실에도 적용되는지 확인
- [ ] 개인전: 봇 턴 자동 진행이 멈추지 않는지(황금열쇠 이동 카드 연쇄 포함) 확인
- [ ] 개인전: 반/번호 → 팀 배정이 규칙대로 일관되는지 확인 (예: 7번 → 7%4 = 3팀)
- [ ] 개인전: SUBMIT_FORM 비어 있을 때 제출 버튼 미노출 확인

## 디자인 가이드 (부루마블 스타일)

### 컨셉
실물 보드게임을 태블릿에 옮긴 느낌. 종이 보드 질감의 밝은 배경, 또렷한 칸 구획, 통통 튀는 말 이동. 장식은 절제하고 "보드게임판"이라는 물성이 바로 읽히게.

### 색 토큰
```css
--board-bg: #f8f4e9;      /* 보드 바탕: 크림(종이 질감) */
--board-frame: #1e3a5f;   /* 보드 외곽 프레임: 딥 네이비 */
--cell-bg: #ffffff;       /* 칸 기본 바탕 */
--cell-line: #d8d2c4;     /* 칸 구분선 */
--center-bg: #eef3ea;     /* 중앙 필드: 연한 그린 */
--gold: #f5c542;          /* 황금열쇠/포인트 강조 */
--team-1: #e53935; --team-2: #1e88e5; --team-3: #fdd835; --team-4: #43a047;
/* 단원 색은 스펙 상단 문제은행의 color 값 사용 */
```

### 칸 스타일 (부루마블 도시칸 구조)
- 도시 칸: **상단 28% 컬러 밴드(구역 색) + 하단 흰 바탕에 국기 이모지 + 도시명 + 가치**. 부루마블 도시칸의 색 띠 구조 그대로. 단원명은 학생에게 절대 노출하지 않음 — 문제만 해당 단원에서 출제.
- 땅 획득 시: 컬러 밴드에 팀 색 깃발(작은 삼각형) 표시 + 칸 바탕이 팀 색 8% 투명도로 물듦.
- 모서리 칸(출발/무인도/세계여행/더블찬스): 1.4배 크기, 아이콘 크게 중앙 배치 (▶ 출발 / 🏝 무인도 / ✈ 세계여행 / ★ 더블찬스), 45도 회전 없이 정방향 유지.
- 황금열쇠 칸: 골드 바탕(#f5c542 20%) + 🔑 아이콘.

### 타이포
- Google Fonts 'Jua' 1개만 로드 (제목·칸 이름·점수용, 보드게임 느낌의 한글 라운드체). 본문은 시스템 폰트 스택.
- 폰트 로드 실패 시 시스템 폰트로 자연스럽게 폴백(레이아웃 어긋나지 않게 line-height 고정). ※ 외부 요청은 이 폰트 1건만 예외 허용.

### 모션 (게임 감각의 핵심)
- **말 이동**: 한 칸씩 순차 hop (칸당 0.15초, translateY 살짝 튀는 easing). 순간이동 금지 — 부루마블 느낌의 80%가 이 애니메이션.
- **주사위**: CSS로 만든 점 눈금 주사위(이미지 없이 div+dot), 0.8초 롤링 후 결과 면 표시.
- **황금열쇠**: 카드 플립(rotateY) 애니메이션으로 공개.
- **정답**: 가벼운 CSS 컨페티(요소 15개 이내) + 점수 카운트업. **오답**: 모달 shake 0.3초.
- prefers-reduced-motion 대응(애니메이션 즉시 완료).

### 레이아웃
- 태블릿 가로 기준: 좌측 정사각 보드(화면 높이 꽉 채움) + 우측 팀 패널 컬럼. 세로 모드: 보드 위, 팀 패널 아래.
- 보드 중앙 필드: 게임 타이틀(Jua) + 주사위 + 현재 팀 표시 + 타이머. 카드가 공개되는 영역도 중앙.
- 문제 모달: 화면 중앙, 보기 버튼 2×2 그리드, 최소 높이 64px, 단원 색 상단 보더로 어느 단원 문제인지 표시.

