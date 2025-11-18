Example 1

> Below is query that need to be tuned
> 

```sql
set statistics time on 
set statistics io on 
set statistics profile on 

-- Practice 
-- USE Three CTE 
WITH MAIN_STYL AS ( 
    SELECT A.fl_CompanyCode
      , A.fl_PLMStyleCode
      , A.fl_PLMStyleColorCode
      , A.fl_PLMStyleSKUCode
    FROM IF_PN_PLM_STYL_SIZE_SKU_RCV_M A -- Common Ref among the CTEs
    INNER JOIN PN_MAIN_STYL_M B
      ON B.COMP_CD = A.fl_CompanyCode
      AND B.PLM_STYL_CD = A.fl_PLMStyleCode
    INNER JOIN PN_MAIN_STYL_CLR_M C
      ON C.COMP_CD = A.fl_CompanyCode  
      AND C.PLM_STYL_CD = A.fl_PLMStyleCode --> Common Ref among CTEs
      AND C.PLM_STYL_CLR_CD = A.fl_PLMStyleColorCode	 -- > Common Ref among CTEs 
    WHERE TSK_PRCS_YN = 'N' --Common Ref among CTEs ( Firtst condition )
      AND (A.fl_StyleSKUMain IS NOT NULL AND A.fl_StyleSKUMain != '') -->  Common Ref among CTEs
),
MAIN_STYL_H AS (
    SELECT A.fl_CompanyCode
      , A.fl_PLMStyleCode
      , A.fl_PLMStyleColorCode
      , A.fl_PLMStyleSKUCode							
    FROM IF_PN_PLM_STYL_SIZE_SKU_RCV_M A -- Common Ref among CTEs
    INNER JOIN PN_MAIN_STYL_H B
      ON B.COMP_CD = A.fl_CompanyCode
      AND B.PLM_STYL_CD = A.fl_PLMStyleCode
    INNER JOIN PN_MAIN_STYL_CLR_H C
      ON C.COMP_CD = A.fl_CompanyCode  
      AND C.PLM_STYL_CD = A.fl_PLMStyleCode
      AND C.PLM_STYL_CLR_CD = A.fl_PLMStyleColorCode
    INNER JOIN ( 
        SELECT COMP_CD, PLM_STYL_CD, MAX(HIST_SEQ) AS HIST_SEQ FROM PN_MAIN_STYL_H -- HIST_SEQ ->It can be fast if there is already sorted data with this becasue find MAX scan all data
        GROUP BY COMP_CD, PLM_STYL_CD 
      ) D
      ON D.COMP_CD = B.COMP_CD
      AND D.PLM_STYL_CD = B.PLM_STYL_CD
      AND D.HIST_SEQ = B.HIST_SEQ
    INNER JOIN ( 
        SELECT COMP_CD, PLM_STYL_CD, PLM_STYL_CLR_CD, MAX(HIST_SEQ) AS HIST_SEQ FROM PN_MAIN_STYL_CLR_H
        GROUP BY COMP_CD, PLM_STYL_CD, PLM_STYL_CLR_CD
      ) E
      ON E.COMP_CD = C.COMP_CD
      AND E.PLM_STYL_CD = C.PLM_STYL_CD
      AND E.PLM_STYL_CLR_CD = C.PLM_STYL_CLR_CD
      AND E.HIST_SEQ = C.HIST_SEQ	
    WHERE TSK_PRCS_YN = 'N' 
      AND (A.fl_StyleSKUMain IS NOT NULL AND A.fl_StyleSKUMain != '')
      AND NOT EXISTS (
        SELECT 1 FROM MAIN_STYL S1
        WHERE S1.fl_CompanyCode = A.fl_CompanyCode
          AND S1.fl_PLMStyleCode = A.fl_PLMStyleCode
          AND S1.fl_PLMStyleColorCode = A.fl_PLMStyleColorCode
          AND S1.fl_PLMStyleSKUCode = A.fl_PLMStyleSKUCode
      )
),
SMPL_STYL AS (
    SELECT A.fl_CompanyCode
      , A.fl_PLMStyleCode
      , A.fl_PLMStyleColorCode
      , A.fl_PLMStyleSKUCode
    FROM IF_PN_PLM_STYL_SIZE_SKU_RCV_M A 
    INNER JOIN PN_SMPL_STYL_M B
      ON B.COMP_CD = A.fl_CompanyCode
      AND B.SMPL_STYL_CD = A.fl_PLMStyleCode
    INNER JOIN PN_SMPL_STYL_CLR_M C
      ON C.COMP_CD = A.fl_CompanyCode  
      AND C.PLM_STYL_CD = A.fl_PLMStyleCode
      AND C.PLM_STYL_CLR_CD = A.fl_PLMStyleColorCode
    WHERE A.TSK_PRCS_YN = 'N' -- 공통 값
      AND (A.fl_StyleSKUMain IS NULL OR A.fl_StyleSKUMain = '')
      AND NOT EXISTS (
        SELECT 1 FROM (
            SELECT fl_CompanyCode, fl_PLMStyleCode, fl_PLMStyleColorCode, fl_PLMStyleSKUCode FROM MAIN_STYL
            UNION ALL
            SELECT fl_CompanyCode, fl_PLMStyleCode, fl_PLMStyleColorCode, fl_PLMStyleSKUCode FROM MAIN_STYL_H
          ) AA
        WHERE AA.fl_CompanyCode = A.fl_CompanyCode
          AND AA.fl_PLMStyleCode = A.fl_PLMStyleCode 
          AND AA.fl_PLMStyleColorCode = A.fl_PLMStyleColorCode
          AND AA.fl_PLMStyleSKUCode = A.fl_PLMStyleSKUCode
        )
)
SELECT TOP 1 (1) FROM (
  SELECT * FROM MAIN_STYL
  UNION
  SELECT * FROM MAIN_STYL_H
  UNION
  SELECT * FROM SMPL_STYL
) 

```

Create IDX can make fast above query

``` sql

CREATE INDEX IX_IF_PN_PLM_STYL_CLR_RCV_M_05 ON [ERP].[dbo].[IF_PN_PLM_STYL_CLR_RCV_M] ([TSK_PRCS_YN], [fl_CompanyCode], [fl_PLMStyleCode], [fl_PLMStyleColorCode],[fl_ColorwaySKUCode]) ON FG_ERP_IDX
```
