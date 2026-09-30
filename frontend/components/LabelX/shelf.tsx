import { useState } from "react";
import { InkButton, SectionLabel, GhostButton, LogoMark } from "./bits";
import { useShelfStore } from "../../store/shelf";

export function ShelfPage() {
  const { products, removeProduct, updatePao } = useShelfStore();
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const calculateDaysLeft = (dateAdded: number, paoMonths: number) => {
    if (paoMonths === 0) return null;
    const expiryDate = new Date(dateAdded);
    expiryDate.setMonth(expiryDate.getMonth() + paoMonths);
    const daysLeft = Math.ceil((expiryDate.getTime() - Date.now()) / (1000 * 60 * 60 * 24));
    return daysLeft;
  };

  return (
    <div className="mx-auto w-full max-w-[800px] animate-rise">
      <header className="mb-10">
        <div className="label-caps mb-2">offline product inventory</div>
        <h2 className="font-display text-3xl font-medium tracking-tight">The Shelf</h2>
        <p className="mt-3 text-[14px] text-inksoft max-w-[500px]">
          Your personalized cosmetic cabinet. Track Period After Opening (PAO) and review your safety analyses anywhere.
        </p>
      </header>

      {products.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-[8px] border-2 border-dashed border-line py-20 text-center">
          <LogoMark size={40} className="mb-4 text-line2" />
          <p className="text-[14px] text-ink font-medium">Your shelf is empty</p>
          <p className="mt-1 text-[13px] text-inksoft">Analyze a product to save it here.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {products.map((product) => {
            const daysLeft = calculateDaysLeft(product.dateAdded, product.paoMonths);
            const isExpanded = expandedId === product.id;

            return (
              <div key={product.id} className="rounded-[8px] border border-line bg-paper2/50 overflow-hidden transition-all">
                <div 
                  className="flex cursor-pointer items-center justify-between p-4 hover:bg-line/20"
                  onClick={() => setExpandedId(isExpanded ? null : product.id)}
                >
                  <div>
                    <h3 className="font-medium text-[15px]">{product.name || "Unnamed Product"}</h3>
                    <p className="text-[12px] text-inksoft mt-1">
                      Added {new Date(product.dateAdded).toLocaleDateString()}
                    </p>
                  </div>
                  
                  <div className="flex items-center gap-4">
                    {daysLeft !== null && (
                      <div className={`text-[12px] font-medium px-2 py-1 rounded-[4px] ${daysLeft < 30 ? 'bg-red-500/10 text-red-600' : 'bg-green-500/10 text-green-600'}`}>
                        {daysLeft < 0 ? "Expired" : `${daysLeft} days left`}
                      </div>
                    )}
                    <button className="text-inksoft hover:text-ink">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={`transition-transform ${isExpanded ? 'rotate-180' : ''}`}>
                        <polyline points="6 9 12 15 18 9"></polyline>
                      </svg>
                    </button>
                  </div>
                </div>

                {isExpanded && (
                  <div className="border-t border-line p-4 space-y-6">
                    <div>
                      <SectionLabel>ingredients</SectionLabel>
                      <p className="mt-2 text-[13px] text-inksoft leading-relaxed">
                        {product.ingredients}
                      </p>
                    </div>

                    <div>
                      <SectionLabel>ai analysis</SectionLabel>
                      <div className="mt-2 rounded-[6px] bg-paper p-4 text-[13px] leading-relaxed text-ink ring-1 ring-line">
                        <div dangerouslySetInnerHTML={{ __html: product.analysisResult.replace(/\n/g, '<br/>') }} />
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-4 border-t border-line/50">
                      <div className="flex items-center gap-3">
                        <label className="text-[12px] font-medium text-inksoft">PAO (Months):</label>
                        <select 
                          value={product.paoMonths}
                          onChange={(e) => updatePao(product.id, parseInt(e.target.value))}
                          className="rounded-[4px] border border-line2 bg-card px-2 py-1 text-[12px] text-ink outline-none"
                        >
                          <option value={0}>None</option>
                          <option value={3}>3M</option>
                          <option value={6}>6M</option>
                          <option value={12}>12M</option>
                          <option value={24}>24M</option>
                        </select>
                      </div>
                      
                      <button 
                        onClick={(e) => { e.stopPropagation(); removeProduct(product.id); }}
                        className="text-[12px] text-red-500 hover:text-red-600 font-medium"
                      >
                        Remove from Shelf
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
