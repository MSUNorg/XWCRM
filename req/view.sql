-- View: xwtest.v_mtgroup

-- DROP VIEW xwtest.v_mtgroup;

CREATE OR REPLACE VIEW xwtest.v_mtgroup AS
 SELECT mt5_groups."Group" AS mtname,
    mt5_groups."DemoLeverage" AS leverage
   FROM mt5_groups
  WHERE "position"(mt5_groups."Group"::text, 'bonus'::text) = 1;

ALTER TABLE xwtest.v_mtgroup
    OWNER TO xwtest;

GRANT ALL ON TABLE xwtest.v_mtgroup TO xwtest;
GRANT ALL ON TABLE xwtest.v_mtgroup TO xw;

-- View: xwtest.v_dealclosed

-- DROP VIEW xwtest.v_dealclosed;

CREATE OR REPLACE VIEW xwtest.v_dealclosed AS
 SELECT dcd."Deal" AS deal,
    dcd."Timestamp" AS "timestamp",
    dcd."Login" AS login,
    dcd."Order" AS "order",
    dcd."Action" AS action,
    dcd."Entry" AS entry,
    dcd."Reason" AS reason,
    dcd."Time" AS "time",
    dcd."Symbol" AS symbol,
    dcd."Price" AS price,
    dcd."Volume" AS volume,
    dcd."Profit" AS profit,
    dcd."Storage" AS storage,
    dcd."Commission" AS commission,
    dcd."RateProfit" AS rateprofit,
    dcd."PositionID" AS positionid,
    dcd."PricePosition" AS priceposition,
    dcd."VolumeClosed" AS volumeclosed
   FROM mt5_deals dcd
  WHERE (dcd."Action" = 0::numeric OR dcd."Action" = 1::numeric) AND NOT (dcd."Timestamp" IN ( SELECT t2.ts
           FROM ( SELECT t1."PositionID" AS pos,
                    min(t1."Timestamp") AS ts
                   FROM mt5_deals t1
                  GROUP BY t1."PositionID") t2));

ALTER TABLE xwtest.v_dealclosed
    OWNER TO xwtest;

GRANT ALL ON TABLE xwtest.v_dealclosed TO xwtest;

-- View: xwtest.v_mtuser

-- DROP VIEW xwtest.v_mtuser;

CREATE OR REPLACE VIEW xwtest.v_mtuser AS
 SELECT t_user.uid,
    mt5_accounts."Login" AS mtlogin,
    mt5_users."Group" AS mtgroup,
    mt5_users."Leverage" AS leverage,
    mt5_accounts."Balance" AS balance,
    mt5_accounts."MarginLevel" AS marginlevel,
    mt5_accounts."Equity" AS equity
   FROM mt5_accounts,
    mt5_users,
    xwtest.t_user
  WHERE (mt5_accounts."Login"::text = ANY (t_user.mtlogin::text[])) AND mt5_users."Login" = mt5_accounts."Login";

ALTER TABLE xwtest.v_mtuser
    OWNER TO xwtest;
COMMENT ON VIEW xwtest.v_mtuser
    IS 'MT账号一览';

GRANT ALL ON TABLE xwtest.v_mtuser TO xwtest;
GRANT ALL ON TABLE xwtest.v_mtuser TO xw;

