**Architecture is designing your data for the questions people will ask.** The most
enduring pattern is **dimensional modeling** (the star schema): slim, reusable
*dimension* tables that describe things (customers, products) and *fact* tables that
record events (orders) at a precise **grain**, linked by keys. Here you build both
halves of a star.
