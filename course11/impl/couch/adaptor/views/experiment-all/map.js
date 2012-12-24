function(doc) { if (doc.doc_type === "Experiment") emit(doc._id, doc.doc_type); }

