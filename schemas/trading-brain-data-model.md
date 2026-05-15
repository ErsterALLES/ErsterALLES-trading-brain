# Trading Brain Data Model Draft

## Core Tables / Objects

### sources

Quelle eines Signals.

Felder:

- `source_id`
- `type`: news, youtube, market_api, social, onchain, sports, macro, earnings, weather
- `name`
- `url`
- `reliability_score`
- `latency_score`
- `manipulation_risk`
- `historical_hit_rate`

### signals

Einzelnes Signal.

Felder:

- `signal_id`
- `source_id`
- `timestamp`
- `asset_or_market`
- `event_id`, optional
- `signal_type`
- `summary`
- `raw_payload_ref`
- `relevance_score`
- `confidence_score`
- `time_sensitivity`
- `directional_bias`: bullish, bearish, neutral, unknown
- `affected_markets`

### events

Übergeordnetes Ereignis.

Felder:

- `event_id`
- `title`
- `category`: geopolitics, earnings, macro, sports, crypto, weather, regulatory
- `start_time`
- `status`: emerging, active, resolved, stale
- `summary`
- `affected_assets`
- `linked_signals`

### video_assets

Trading-Videos oder Kurse.

Felder:

- `video_id`
- `source_id`
- `url`
- `title`
- `channel`
- `duration`
- `local_file_path`
- `transcript_status`
- `frame_status`
- `strategy_extraction_status`

### transcript_segments

Timestamped Transkriptsegmente.

Felder:

- `segment_id`
- `video_id`
- `start_time`
- `end_time`
- `text`
- `topic`
- `linked_frames`

### visual_evidence

Analysierte Frames/Screenshots.

Felder:

- `frame_id`
- `video_id`
- `timestamp`
- `image_path`
- `detected_market`
- `detected_timeframe`
- `detected_indicators`
- `chart_pattern`
- `entry_marker`
- `exit_marker`
- `stop_marker`
- `analysis_json`

### strategy_components

Wiederverwendbare Strategiebausteine.

Felder:

- `component_id`
- `name`
- `type`: setup, entry, exit, risk, filter, invalidation, session, management
- `description`
- `rules`
- `evidence_refs`
- `source_video_refs`
- `confidence_score`

### strategies

Konkrete Strategie-Version.

Felder:

- `strategy_id`
- `name`
- `version`
- `market_scope`
- `timeframes`
- `components`
- `entry_rules`
- `exit_rules`
- `risk_rules`
- `filters`
- `invalidations`
- `status`: draft, backtesting, shadow, live-small, live-scaled, retired

### trade_ideas

Noch nicht ausgeführte Trade-Ideen.

Felder:

- `idea_id`
- `timestamp`
- `strategy_id`
- `market`
- `direction`
- `thesis`
- `confidence`
- `expected_edge`
- `risk_level`
- `suggested_size`
- `required_confirmations`
- `status`

### positions

Aktive Trades.

Felder:

- `position_id`
- `strategy_id`
- `market`
- `entry_time`
- `entry_price`
- `size`
- `stop_loss`
- `take_profit`
- `current_pnl`
- `risk_at_entry`
- `current_status`

### trade_outcomes

Abgeschlossene Trades und Lernmaterial.

Felder:

- `outcome_id`
- `position_id`
- `exit_time`
- `exit_price`
- `pnl`
- `r_multiple`
- `win_loss`
- `what_worked`
- `what_failed`
- `signals_confirmed`
- `signals_invalidated`
- `strategy_adjustments`

## Graph-Beziehungen

- source → signals
- signals → events
- video_assets → transcript_segments
- video_assets → visual_evidence
- transcript_segments ↔ visual_evidence
- visual_evidence → strategy_components
- strategy_components → strategies
- strategies → trade_ideas
- trade_ideas → positions
- positions → trade_outcomes
- trade_outcomes → strategy_updates
